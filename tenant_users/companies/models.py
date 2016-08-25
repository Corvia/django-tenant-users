import time
from django.db import models
from django.db import connection
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    Permission, Group
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from ..compat import TenantMixin
from ..compat import get_public_schema_name, get_tenant_model

from ..permissions.models import UserTenantPermissions, \
    PermissionsMixinFacade

from ..permissions.roles import PUBLIC_ROLE_DEFAULT

class InactiveError(Exception):
    pass

class RoleError(Exception):
    pass

class ExistsError(Exception):
    pass

class DeleteError(Exception):
    pass

class SchemaError(Exception):
    pass

class TenantBase(TenantMixin):
    """
    Contains global data and settings for the tenant model.
    """
    slug = models.SlugField(_('Tenant URL Name'), blank=True)

    # The owner of the tenant. Only they can delete it. This can be changed, but it
    # can't be blank. There should always be an owner.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True)

    # Schema will be automatically created and synced when it is saved
    auto_create_schema = True
    # Schema will be automatically deleted when related tenant is deleted
    auto_drop_schema = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()

        super(TenantBase, self).save(*args, **kwargs)

    def delete(self, force_drop=False):
        if force_drop:
            super(TenantBase, self).delete(force_drop=True)
        else:
            raise DeleteError("Not supported -- delete_tenant() should be used.")

    def _validate_app(self, app_name):
        '''
        Internal helper function to make sure the specified app actually exists 
        '''
        if not ContentType.objects.filter(app_label=app_name).first():
            raise DoesNotExist('App: %s not found in ContentTypes', app_name)
    
    
    def _get_group(self, group_name):
        '''
        Internal helper function to return a group from the group name 
        '''
        group = Group.objects.filter(name=group_name).first()
        if not group:
            raise DoesNotExist('Group: %s does not exist', group_name)
        return group
    
    
    def _get_permission(self, perm, content_type):
        '''
        Internal helper function to return the permission object matching
        the specified permission and content type in the current scehema
        '''
        codename = "{}_{}".format(perm, content_type.model)
        permission = Permission.objects.filter(
            codename=codename, 
            content_type=content_type,
        ).first()
        if not permission:
            raise DoesNotExist('Permission: %s does not exist', perm)
        return permission
    
    
    def _assign_role_permissions_by_app(self, group_name, app_name, permissions):
        '''
        Internal helper function to iteratve over all models inside an app
        and assign the given permissions of those models to the group specified
        all inside the currently selected schema
        '''
        self._validate_app(app_name)
        group = self._get_group(group_name)
    
        content_types = ContentType.objects.filter(app_label=app_name).all()
        for content_type in content_types:
            for perm in permissions:
                permission_obj = self._get_permission(perm, content_type)
                # Don't create the permission on the group if it already exists
                if group.permissions.filter(id=permission_obj.id).first():
                    continue
                group.permissions.add(permission_obj)
    
    
    def _create_group(self, group_name):
        '''
        Internal helper function to create a group if it doesn't exist 
        inside the current schema
        '''
        group = Group.objects.filter(name=group_name).first()
        if group:
            return
        Group.objects.create(name=group_name)
    
    
    # NOTE: this function could take some time to run if several roles are being
    # assigned. Consider using it asynchronously in a celery task if this is run
    # in a request
    def create_roles(self, role_definitions):
        '''
        This function iterates over role definitions, creates them if they don't
        already exist and assigns all default permissions specified in those roles
        on a given tenant. see roles.py for role_definitions structure 
        '''
        tenant_schema = self.schema_name
    
        # Save current schema and restore it when we're done
        saved_schema = connection.get_schema()
        # Set schema to this tenants schema to start building permissions in that tenant
        connection.set_schema(tenant_schema)
    
        try:
            for group_name,app_list in role_definitions.items():
                self._create_group(group_name)
                for app in app_list: 
                    self._assign_role_permissions_by_app(group_name, app['app'], app['permissions'])
        finally:
            # Even if an exception is raised we need to reset our schema state
            connection.set_schema(saved_schema)
    
    def assign_user_role(self, user_obj, role_name, allow_owner=False):
        '''
        Tenant and user must exist. Role must be a valid role.
        If user is not linked to the tenant yet we need to set up all the tenant 
        scaffolding for user permissions. We also need to link the permissions
        to the user and the user to the tenant. If the user is already linked to
        a tenant, we assume that's all already setup and we just assign the role
        if it's not already assigned. 
        Do nothing if the user is the tenant owner unless allow_owner parameter is 
        specified This should be only in special circumstances such as provisioning.
        '''
        tenant_schema = self.schema_name

        if not user_obj.is_active:
            raise InactiveError("Can't assign inactive user to tenant role")
    
        # Do nothing if the user is the tenant owner unless allow_owner parameter is specified
        # This should be only in special circumstances such as provisioning
        if not allow_owner and user_obj.id == self.owner.id:
            raise RoleError("Can't assign additional roles to the tenant owner")
    
        # Save current schema and restore it when we're done
        saved_schema = connection.get_schema()
        # Set schema to this tenants schema to start building permissions in that tenant
        connection.set_schema(tenant_schema)
    
        try:
            group = self._get_group(role_name)
    
            if not self.user_set.filter(id=user_obj.id).exists():
                # User not linked to this tenant, so we need to create tenant permissions
                user_tenant_perms = UserTenantPermissions.objects.create(
                    profile=user_obj,
                    is_staff=False, 
                    is_superuser=False
                )
                # Link user to tenant 
                user_obj.tenants.add(self)
                # Assign role if not already assigned
                user_tenant_perms.groups.add(group)
            else:
                # User is already linked, assign a role. Tenant Perms should already exist
                # Assign new role privileges to the user if not yet assigned
                # there should only be one user tenant permissions in the set
                user_tenant_perms = user_obj.usertenantpermissions_set.first()
                if user_tenant_perms.groups.filter(name=role_name).exists():
                    raise RoleError("User already has the specified role")
                # Assign role if not already assigned
                user_tenant_perms.groups.add(group)
        finally:
            connection.set_schema(saved_schema)
    
    def revoke_user_role(self, user_obj, role_name=None, allow_owner=False):
        '''
        Tenant and user must exist. If no role is passed, all roles are deleted.
        If the user specified is the owner of the tenant, by default nothing happens 
        (only has admin role, and that can't be revoked). Must specify allow_owner
        to override and allow an owner's role to be revoked. This should only be
        specified in special cases, such as during delete_tenant
        If the user has no remaining roles on the tenant, we then delete the tenant
        permissions entry reflecting that user and unlink the user from the tenant
        altogether at the global level.
        '''
        tenant_schema = self.schema_name
    
        # if user is the tenant.owner, and allow_owner not specified, do nothing
        if not allow_owner and self.owner.id == user_obj.id:
            raise RoleError("Cannot revoke roles from a tenant's owner")
    
        # Save current schema and restore it when we're done
        saved_schema = connection.get_schema()
        # Set schema to this tenants schema to start building permissions in that tenant
        connection.set_schema(tenant_schema)
    
        try:
            # if user is NOT linked to the tenant
            if not self.user_set.filter(id=user_obj.id).exists():
                raise DoesNotExist("User does not exist on the tenant specified")
    
            user_tenant_perms = user_obj.usertenantpermissions_set.first()
            groups = user_tenant_perms.groups
        
            if not role_name:
                # clear all roles if none specified
                groups.clear()
            else:
                group = groups.filter(name=role_name)
                if not group.exists():
                    raise RoleError("User does not have specified role on tenant")
                groups.remove(group.first())
    
            # If no roles remain on the tenant for the user delete tenant 
            # permissions and unlink the user from the tenant 
            if not groups.exists():
                UserTenantPermissions.objects.filter(id=user_tenant_perms.id).delete()
                # Unlink from tenant
                user_obj.tenants.remove(self)
        finally:
            connection.set_schema(saved_schema)
    
    def get_current_roles(self, user_obj):
        '''
        Returns a list of Group objects designating the roles that the user has
        on the given tenant.
        '''
        tenant_schema = self.schema_name
    
        # Save current schema and restore it when we're done
        saved_schema = connection.get_schema()
        # Set schema to this tenants schema to start building permissions in that tenant
        connection.set_schema(tenant_schema)
    
        try:
            user_tenant_perms = user_obj.usertenantpermissions_set.first()
            groups = [group.name for group in user_tenant_perms.groups.all()]
        finally:
            connection.set_schema(saved_schema)
    
        # We don't want to return a queryset or pass objects from the tenant schema
        # Because when the schema gets reset it will no longer be valid. So instead
        # We return a list of role names
        return groups
    
    def delete_tenant(self):
        '''
        We don't actually delete the tenant out of the database, but we associate them
        with a the public schema user and change their url to reflect their delete 
        datetime and previous owner
        The caller should verify that the user deleting the tenant owns the tenant.
        '''
        # Prevent public tenant schema from being deleted
        if self.schema_name == get_public_schema_name():
            raise ValueError("Cannot delete public tenant schema")

        for user_obj in self.user_set.all():
            # All roles will be revoked since none specified. All
            # users will be unlinked from the tenant
            self.revoke_user_role(user_obj, None, True)
    
        # Seconds since epoch, time() returns a float, so we convert to 
        # an int first to truncate the decimal portion
        time_string = str(int(time.time()))
        new_url = "{}-{}-{}".format(
            time_string,
            str(self.owner.id),
            self.domain_url
        )
        self.domain_url = new_url
        # The schema generated each time (even with same url slug) will be unique.
        # So we do not have to worry about a conflict with that
    
        # Set the owner to the system user (public schema owner)
        public_tenant = get_tenant_model().objects.get(schema_name=get_public_schema_name())
        self.owner = public_tenant.owner 
        self.save()
        
    class Meta:
        abstract = True


class UserProfileManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        # Do some schema validation to protect against calling create user from inside
        # a tenant. Must create public tenant permissions during user creation. This
        # happens during assign role. This function cannot be used until a public
        # schema already exists
        UserModel = get_user_model()

        if connection.get_schema() != get_public_schema_name():
            raise SchemaError("Schema must be public for UserProfileManager user creation")

        if not email:
            raise ValueError("Users must have an email address.")

        # If no password is submitted, just assign a random one to lock down
        # the account a little bit.
        if not password:
            password = self.make_random_password(length=30)

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
        if not profile:
            profile = UserModel()

        profile.email = email
        profile.is_active = True
        profile.set_password(password)
        profile.save()
        
        # Get public tenant tenant and assign empty use role here to link user
        # to the public tenant, and create tenant permissions entry 
        public_tenant = get_tenant_model().objects.get(schema_name=get_public_schema_name())
        public_tenant.assign_user_role(profile, PUBLIC_ROLE_DEFAULT, True)
        
        # Public tenant permissions object was created when we assigned a
        # role to the user above, if we are a staff/superuser we set it here
        if is_staff or is_superuser:
            user_tenant = profile.usertenantpermissions_set.first()
            user_tenant.is_staff = is_staff
            user_tenant.is_superuser = is_superuser
            user_tenant.save()

        return profile

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, password, email=None, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def delete_user(self, user_obj):
        if not user_obj.is_active:
            raise InactiveError("User specified is not an active user!")

        # Check to make sure we don't try to delete the public tenant owner
        # that would be bad....
        public_tenant = get_tenant_model().objects.get(schema_name=get_public_schema_name())
        if user_obj.id == public_tenant.owner.id:
            raise DeleteError("Cannot delete the public tenant owner!")

        # This includes the linked public tenant 'tenant'. It will delete the
        # Tenant permissions and unlink when user is deleted
        for tenant in user_obj.tenants.all():
            # Unlink user from all roles in any tenant it doesn't own
            # Specify true to allow any tenants that this user owns
            # without erroring. Don't specify role to revoke all
            tenant.revoke_user_role(user_obj, None, True)

            # If user owns the tenant, we need to call delete on the tenant
            if tenant.owner.id == user_obj.id:
                # Delete tenant will handle any other linked users to that tenant
                tenant.delete_tenant()

        # Set is_active, don't actually delete the object
        user_obj.is_active = False
        user_obj.save()


# This cant be located in the users app otherwise it would get loaded into
# both the public schema and all tenant schemas. We want profiles only
# in the public schema alongside the TenantBase model 
class UserProfile(AbstractBaseUser, PermissionsMixinFacade):
    """
    An authentication-only model that is in the public tenant schema but 
    linked from the authorization model (UserTenantPermissions)
    where as to allow for one global profile (public schema) for each user
    but maintain permissions on a per tenant basis.
    To access permissions for a user, the request must come through the
    tenant that permissions are desired for. 
    Requires use of the ModelBackend
    """

    USERNAME_FIELD = "email"
    objects = UserProfileManager()

    tenants = models.ManyToManyField(
        settings.TENANT_MODEL,
        verbose_name=_('tenants'),
        blank=True,
        help_text=_('The tenants this user belongs to.'),
        related_name="user_set"
    )

    email = models.EmailField(
        _("Email Address"),
        unique = True,
        db_index = True,
    )

    is_active = models.BooleanField(default = True)

    class Meta:
        abstract = True

    def delete(self, force_drop=False):
        if force_drop:
            super(UserProfile, self).delete(force_drop=True)
        else:
            raise DeleteError("UserProfile.objects.delete_user() should be used.")

    def __unicode__(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return str(self)  # just use __unicode__ here.
