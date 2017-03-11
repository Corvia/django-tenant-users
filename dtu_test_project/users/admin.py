from django.contrib import admin
from users.models import TenantUser

@admin.register(TenantUser)
class UserProfileAdmin(admin.ModelAdmin):
    pass
