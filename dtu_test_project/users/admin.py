from django.contrib import admin
from users.models import TenantUser

from tenant_users.permissions.models import UserTenantPermissions


@admin.register(TenantUser)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTenantPermissions)
class UserTenantPermissionsAdmin(admin.ModelAdmin):
    pass
