from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

class PermissionsMixinFacade(object):
    '''
    This class is designed to shim the PermissionMixin class functions and
    delegate them down to the correct linked (based on the current schema)
    tenant permissions since we don't handle them in the user like stock
    django does. This is designed to be inherited from by the AUTH_USER_MODEL
    '''
    class Meta:
        abstract = True

    # This will throw a DoesNotExist exception if there is no tenant
    # permissions matching the current schema, which means that this
    # user has no authorization, so we catch this exception and return
    # the appropriate False or empty set
    def _get_tenant_perms(self):
        return UserTenantPermissions.objects.get(profile_id=self.id)

    @property
    def is_staff(self):
        try:
            return self._get_tenant_perms().is_staff
        except UserTenantPermissions.DoesNotExist:
            return False

    @property
    def is_superuser(self):
        try:
            return self._get_tenant_perms().is_superuser
        except UserTenantPermissions.DoesNotExist:
            return False

    def get_group_permissions(self, obj=None):
        try:
            return self._get_tenant_perms().get_group_permissions(obj) 
        except UserTenantPermissions.DoesNotExist:
            return set()

    def get_all_permissions(self, obj=None):
        try:
            return self._get_tenant_perms().get_all_permissions(obj)        
        except UserTenantPermissions.DoesNotExist:
            return set()

    def has_perm(self, perm, obj=None):
        try:
            return self._get_tenant_perms().has_perm(obj)  
        except UserTenantPermissions.DoesNotExist:
            return False

    def has_perms(self, perm_list, obj=None):
        try:
            return self._get_tenant_perms().has_perms(perm_list, obj)  
        except UserTenantPermissions.DoesNotExist:
            return False

    def has_module_perms(self, app_label):
        try:
            return self._get_tenant_perms().has_module_perms(app_label)
        except UserTenantPermissions.DoesNotExist:
            return False


class AbstractBaseUserFacade(object):
    '''
    This class is designed to shim functions on the authorization model
    that are actually part of the authentication model. Auth backends
    expect the models to be combined, but we separate them so we can
    have single authentication across the system, but have per
    tenant permissions
    '''
    class Meta:
        abstract = True

    @property
    def is_active(self):
        return self.profile.is_active

    @property
    def is_anonymous(self):
        return False
    

class UserTenantPermissions(PermissionsMixin, AbstractBaseUserFacade):
    '''
    This class serves as the authorization model (permissions) per-tenant.
    We keep all of the global user profile information in the public tenant
    schema including authentication aspects. See UserProfile model.
    '''
    # The profile stores all of the common information between tenants for a user
    profile = models.OneToOneField(settings.AUTH_USER_MODEL)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this tenants '
                    'admin site.'))
