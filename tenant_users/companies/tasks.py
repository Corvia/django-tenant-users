import time
from django.conf import settings
from django.contrib.auth import get_user_model
from ..compat import get_tenant_model

from .models import InactiveError, ExistsError
from ..permissions.roles import TENANT_DEFAULT_ROLES, TENANT_ROLE_ADMIN

def provision_tenant(tenant_name, tenant_slug, user_email):
    """Create a tenant with default roles and permissions

    Returns:
    The FQDN for the tenant.
    """
    tenant = None

    UserModel = get_user_model()
    TenantModel = get_tenant_model()

    user = UserModel.objects.get(email=user_email)
    if not user.is_active:
        raise InactiveError("Inactive user passed to provision tenant")

    tenant_domain = '{}.{}'.format(tenant_slug, settings.TENANT_USERS_DOMAIN)

    if TenantModel.objects.filter(domain_url=tenant_domain).first():
        raise ExistsError("Tenant URL already exists")

    time_string = str(int(time.time()))
    # Must be valid postgres schema characters see:
    # https://www.postgresql.org/docs/9.2/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    # We generate unique schema names each time so we can keep tenants around without
    # taking up url/schema namespace. 
    schema_name = '{}_{}'.format(tenant_slug, time_string)

    try:
        # Create a TenantModel object and tenant schema
        tenant = TenantModel.objects.create(
            name=tenant_name,
            slug=tenant_slug,
            domain_url=tenant_domain, 
            schema_name=schema_name,
            owner = user,
        )

        if hasattr(settings, "TENANT_DEFAULT_ROLES"):
            default_roles = settings.TENANT_DEFAULT_ROLES
        else:
            default_roles = TENANT_DEFAULT_ROLES

        # Create the default roles and permissions inside the tenant
        tenant.create_roles(default_roles)

        # Set user to admin role on the tenant 
        tenant.assign_user_role(user, TENANT_ROLE_ADMIN, True)
    except:
        if tenant is not None:
            #Flag is set to auto-drop the schema for the tenant
            tenant.delete(True)
        raise

    return tenant_domain
