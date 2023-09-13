from django.apps import AppConfig


class TenantsConfig(AppConfig):
    """Configuration for tenant_users.tenants app."""

    default_auto_field = "django.db.models.AutoField"
    name = "tenant_users.tenants"
    label = "tenant_users_tenants"
