import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import connection, models
from django.dispatch import Signal
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin
from django_tenants.utils import get_public_schema_name, get_tenant_model

from tenant_users.permissions.models import (
    PermissionsMixinFacade,
    UserTenantPermissions,
)

# An existing user removed from a tenant
tenant_user_removed = Signal()

# An existing user added to a tenant
tenant_user_added = Signal()

# A new user is created
tenant_user_created = Signal()

# An existing user is deleted
tenant_user_deleted = Signal()

TENANT_DELETE_ERROR_MESSAGE = (
    "calling delete on tenant instance is not supported, call delete_tenant instead"
)


class InactiveError(Exception):
    pass


class ExistsError(Exception):
    pass


class DeleteError(Exception):
    pass


class SchemaError(Exception):
    pass


def schema_required(func):
    def inner(self, *args, **options):
        tenant_schema = self.schema_name
        # Save current schema and restore it when we're done
        saved_schema = connection.schema_name
        # Set schema to this tenants schema to start building permissions
        # in that tenant
        connection.set_schema(tenant_schema)
        try:
            result = func(self, *args, **options)
        finally:
            # Even if an exception is raised we need to reset our schema state
            connection.set_schema(saved_schema)
        return result

    return inner


class TenantBase(TenantMixin):
    """Contains global data and settings for the tenant model."""

    slug = models.SlugField(_("Tenant URL Name"), blank=True)

    # The owner of the tenant. Only they can delete it. This can be changed,
    # but it can't be blank. There should always be an owner.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Schema will be automatically created and synced when it is saved
    auto_create_schema = True
    # Schema will be automatically deleted when related tenant is deleted
    auto_drop_schema = True

    def delete(self, *args, force_drop: bool = False, **kwargs):
        """Override deleting of Tenant object.

        Args:
            force_drop (bool): If True, forces the deletion of the object. Defaults to False.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if force_drop:
            super().delete(force_drop, *args, **kwargs)
        else:
            raise DeleteError(TENANT_DELETE_ERROR_MESSAGE)

    @schema_required
    def add_user(self, user_obj, *, is_superuser: bool = False, is_staff: bool = False):
        """Add user to tenant.

        Args:
            user_obj: The user object to be added to the tenant.
            is_superuser (bool): If True, assigns superuser privileges to the user. Defaults to False.
            is_staff (bool): If True, assigns staff status to the user. Defaults to False.
        """
        # User already is linked here..
        if self.user_set.filter(id=user_obj.pk).exists():
            raise ExistsError(
                f"User already added to tenant: {user_obj}",
            )

        # User not linked to this tenant, so we need to create
        # tenant permissions
        UserTenantPermissions.objects.create(
            profile=user_obj,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        # Link user to tenant
        user_obj.tenants.add(self)

        tenant_user_added.send(
            sender=self.__class__,
            user=user_obj,
            tenant=self,
        )

    @schema_required
    def remove_user(self, user_obj):
        """Remove user from tenant."""
        # Test that user is already in the tenant
        self.user_set.get(pk=user_obj.pk)

        # Dont allow removing an owner from a tenant. This must be done
        # Through delete tenant or transfer_ownership
        if user_obj.pk == self.owner.pk:
            raise DeleteError(
                f"Cannot remove owner from tenant: {self.owner}",
            )

        user_tenant_perms = user_obj.usertenantpermissions
        # Remove all current groups from user..
        groups = user_tenant_perms.groups
        groups.clear()

        # Unlink from tenant
        UserTenantPermissions.objects.filter(pk=user_tenant_perms.pk).delete()
        user_obj.tenants.remove(self)
        # Remove tenant specific cached attributes
        if self.schema_name in user_obj.__dict__:
            del user_obj.__dict__[self.schema_name]

        tenant_user_removed.send(
            sender=self.__class__,
            user=user_obj,
            tenant=self,
        )

    def delete_tenant(self):
        """Mark tenant for deletion.

        We don't actually delete the tenant out of the database, but we
        associate them with a the public schema user and change their url
        to reflect their delete datetime and previous owner
        The caller should verify that the user deleting the tenant owns
        the tenant.
        """
        # Prevent public tenant schema from being deleted
        if self.schema_name == get_public_schema_name():
            raise ValueError("Cannot delete public tenant schema")

        for user_obj in self.user_set.all():
            # Don't delete owner at this point
            if user_obj.pk == self.owner.pk:
                continue
            self.remove_user(user_obj)

        # Seconds since epoch, time() returns a float, so we convert to
        # an int first to truncate the decimal portion
        time_string = str(int(time.time()))
        new_url = f"{time_string}-{self.owner.pk!s}-{self.domain_url}"
        self.domain_url = new_url
        # The schema generated each time (even with same url slug) will
        # be unique so we do not have to worry about a conflict with that

        # Set the owner to the system user (public schema owner)
        public_tenant = get_tenant_model().objects.get(
            schema_name=get_public_schema_name(),
        )

        old_owner = self.owner

        # Transfer ownership to system
        self.transfer_ownership(public_tenant.owner)

        # Remove old owner as a user if the owner still exists after
        # the transfer
        if self.user_set.filter(pk=user_obj.pk).exists():
            self.remove_user(old_owner)

    @schema_required
    def transfer_ownership(self, new_owner):
        old_owner = self.owner

        # Remove current owner superuser status but retain any assigned role(s)

        old_owner_tenant_permissions = old_owner.usertenantpermissions
        old_owner_tenant_permissions.is_superuser = False
        old_owner_tenant_permissions.save(update_fields=["is_superuser"])

        self.owner = new_owner

        # If original has no permissions left, remove user from tenant
        if not old_owner_tenant_permissions.groups.exists():
            self.remove_user(old_owner)

        try:
            # Set new user as superuser in this tenant if user already exists
            user = self.user_set.get(pk=new_owner.pk)
            user_tenant = user.usertenantpermissions
            user_tenant.is_superuser = True
            user_tenant.save(update_fields=["is_superuser"])
        except get_user_model().DoesNotExist:
            # New user is not a part of the system, add them as a user..
            self.add_user(new_owner, is_superuser=True)

        self.save(update_fields=["owner"])

    class Meta:
        abstract = True


class UserProfileManager(BaseUserManager):
    def _create_user(  # noqa: PLR0913
        self,
        email,
        password,
        is_staff,
        is_superuser,
        is_verified,
        **extra_fields,
    ):
        # Do some schema validation to protect against calling create user from
        # inside a tenant. Must create public tenant permissions during user
        # creation. This happens during assign role. This function cannot be
        # used until a public schema already exists
        UserModel = get_user_model()  # noqa: N806

        if connection.schema_name != get_public_schema_name():
            raise SchemaError(
                "Schema must be public for UserProfileManager user creation",
            )

        if not email:
            raise ValueError("Users must have an email address.")

        email = self.normalize_email(email)

        profile = UserModel.objects.filter(email=email).first()
        if profile and profile.is_active:
            raise ExistsError("User already exists!")

        # Profile might exist but not be active. If a profile does exist
        # all previous history logs will still be associated with the user,
        # but will not be accessible because the user won't be linked to
        # any tenants from the user's previous membership. There are two
        # exceptions to this. 1) The user gets re-invited to a tenant it
        # previously had access to (this is good thing IMO). 2) The public
        # schema if they had previous activity associated would be available
        profile = profile if profile else UserModel()
        profile.email = email

        profile.is_active = True
        profile.is_verified = is_verified
        profile.set_password(password)
        for attr, value in extra_fields.items():
            setattr(profile, attr, value)
        profile.save()

        # Get public tenant tenant and link the user (no perms)
        public_tenant = get_tenant_model().objects.get(
            schema_name=get_public_schema_name(),
        )
        public_tenant.add_user(profile)

        # Public tenant permissions object was created when we assigned a
        # role to the user above, if we are a staff/superuser we set it here
        if is_staff or is_superuser:
            user_tenant = profile.usertenantpermissions
            user_tenant.is_staff = is_staff
            user_tenant.is_superuser = is_superuser
            user_tenant.save()

        tenant_user_created.send(sender=self.__class__, user=profile)

        return profile

    def create_user(
        self,
        email=None,
        password=None,
        *,
        is_staff: bool = False,
        **extra_fields,
    ):
        user = self._create_user(
            email,
            password,
            is_staff,
            is_superuser=False,
            is_verified=False,
            **extra_fields,
        )

        if not password:
            user.set_unusable_password()

        return user

    def create_superuser(self, password, email=None, **extra_fields):
        return self._create_user(
            email,
            password,
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            **extra_fields,
        )

    def delete_user(self, user_obj):
        # Check to make sure we don't try to delete the public tenant owner
        # that would be bad....
        public_tenant = get_tenant_model().objects.get(
            schema_name=get_public_schema_name(),
        )
        if user_obj.pk == public_tenant.owner.pk:
            raise DeleteError("Cannot delete the public tenant owner!")

        # This includes the linked public tenant 'tenant'. It will delete the
        # Tenant permissions and unlink when user is deleted
        for tenant in user_obj.tenants.all():
            # If user owns the tenant, we call delete on the tenant
            # which will delete the user from the tenant as well
            if tenant.owner.pk == user_obj.pk:
                # Delete tenant will handle any other linked users to
                # that tenant
                tenant.delete_tenant()
            else:
                # Unlink user from all roles in any tenant it doesn't own
                tenant.remove_user(user_obj)

        # Set is_active, don't actually delete the object
        user_obj.is_active = False
        user_obj.save(update_fields=["is_active"])

        tenant_user_deleted.send(sender=self.__class__, user=user_obj)


# This cant be located in the users app otherwise it would get loaded into
# both the public schema and all tenant schemas. We want profiles only
# in the public schema alongside the TenantBase model
class UserProfile(AbstractBaseUser, PermissionsMixinFacade):
    """Authentication model for django-tenant-users stored in the public tenant schema.

    This class represents an authentication-only model that is centrally located in the public tenant schema,
    yet maintains a link to the UserTenantPermissions model for authorization. It enables a singular global
    user profile across all tenants while allowing permissions to be managed on a per-tenant basis. This design
    ensures a unified user identity across different tenants with distinct permission sets in each tenant context.

    Access to a user's permissions requires routing the request through the relevant tenant. The implementation
    necessitates using the ModelBackend for proper integration.

    Inherits:
        AbstractBaseUser: Django's base class for user models, providing core user authentication features.
        PermissionsMixinFacade: A facade to adapt Django's PermissionMixin for multi-tenant environments.
    """

    USERNAME_FIELD = "email"
    objects = UserProfileManager()

    tenants = models.ManyToManyField(
        settings.TENANT_MODEL,
        verbose_name=_("tenants"),
        blank=True,
        help_text=_("The tenants this user belongs to."),
        related_name="user_set",
    )

    email = models.EmailField(
        _("Email Address"),
        unique=True,
        db_index=True,
    )

    is_active = models.BooleanField(_("active"), default=True)

    # Tracks whether the user's email has been verified
    is_verified = models.BooleanField(_("verified"), default=False)

    class Meta:
        abstract = True

    def has_verified_email(self):
        return self.is_verified

    def delete(self, *args, force_drop: bool = False, **kwargs):
        if force_drop:
            super().delete(*args, **kwargs)
        else:
            raise DeleteError(
                "UserProfile.objects.delete_user() should be used.",
            )

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        """Return string representation."""
        return str(self)
