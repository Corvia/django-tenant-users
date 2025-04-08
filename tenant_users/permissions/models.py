from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from tenant_users.permissions.functional import tenant_cached_property


class PermissionsMixinFacade:
    """A facade for Django's PermissionMixin to handle multi-tenant permissions.

    Adapts Django's PermissionMixin to work seamlessly with django-tenant-users, by
    delegating permission-related functionalities to the tenant-specific permissions model.
    It ensures that permissions are correctly managed according to the tenant context,
    rather than using Django's default user-based permission system.

    Note:
        This class is abstract and should be inherited by AUTH_USER_MODEL.
    """

    class Meta:
        abstract = True

    # This will throw a DoesNotExist exception if there is no tenant
    # permissions matching the current schema, which means that this
    # user has no authorization, so we catch this exception and return
    # the appropriate False or empty set
    @tenant_cached_property
    def tenant_perms(self):
        return UserTenantPermissions.objects.get(
            profile_id=self.pk,
        )

    def has_tenant_permissions(self) -> bool:
        try:
            _ = self.tenant_perms
        except UserTenantPermissions.DoesNotExist:
            return False

        return True

    @tenant_cached_property
    def is_staff(self):
        try:
            return self.tenant_perms.is_staff
        except UserTenantPermissions.DoesNotExist:
            return False

    @tenant_cached_property
    def is_superuser(self):
        try:
            return self.tenant_perms.is_superuser
        except UserTenantPermissions.DoesNotExist:
            return False

    def get_group_permissions(self, obj=None):
        try:
            return self.tenant_perms.get_group_permissions(obj)
        except UserTenantPermissions.DoesNotExist:
            return set()

    def get_all_permissions(self, obj=None):
        try:
            return self.tenant_perms.get_all_permissions(obj)
        except UserTenantPermissions.DoesNotExist:
            return set()

    def has_perm(self, perm, obj=None):
        try:
            return self.tenant_perms.has_perm(perm, obj)
        except UserTenantPermissions.DoesNotExist:
            return False

    def has_perms(self, perm_list, obj=None):
        try:
            return self.tenant_perms.has_perms(perm_list, obj)
        except UserTenantPermissions.DoesNotExist:
            return False

    def has_module_perms(self, app_label):
        try:
            return self.tenant_perms.has_module_perms(app_label)
        except UserTenantPermissions.DoesNotExist:
            return False


class AbstractBaseUserFacade:
    """A facade class bridging authorization and authentication models in a multi-tenant setup.

    In django-tenant-users, authentication and authorization models are separated to enable
    single authentication with per-tenant permissions. This class acts as a shim, aligning
    functions typically found in the authentication model with those expected by Django's
    auth backends. It ensures compatibility and functionality in scenarios where auth backends
    expect a combined model structure.
    """

    class Meta:
        abstract = True

    @property
    def is_active(self):
        return self.profile.is_active

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return self.profile.is_authenticated


class UserTenantPermissions(PermissionsMixin, AbstractBaseUserFacade):
    """Authorization model for managing per-tenant permissions in Django-tenant-users.

    This class is responsible for handling the authorization aspects (permissions) for each tenant.
    It complements the UserProfile model, which stores global user profile information and authentication
    details in the public tenant schema. By separating authorization on a per-tenant basis, this model
    supports a flexible and scalable approach to permissions management in a multi-tenant environment.

    Inherits:
        PermissionsMixin: Provides Django's built-in permissions framework.
        AbstractBaseUserFacade: Bridges authorization with authentication models.

    See Also:
        UserProfile: For the model handling global user profile and authentication aspects.
    """

    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name="ID",
    )

    # The profile stores all of the common information between
    # tenants for a user
    profile = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this tenants admin site.",
        ),
    )

    def __str__(self):
        """Return string representation."""
        return str(self.profile)
