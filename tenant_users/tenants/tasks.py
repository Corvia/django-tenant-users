import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django_tenants.utils import (
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    schema_context,
)

from tenant_users.tenants.models import ExistsError, InactiveError


def provision_tenant(tenant_name, tenant_slug, user_email, is_staff=False):
    """Create a tenant with default roles and permissions.

    Returns:
    The FQDN for the tenant.
    """
    tenant = None

    UserModel = get_user_model()
    TenantModel = get_tenant_model()

    user = UserModel.objects.get(email=user_email)
    if not user.is_active:
        raise InactiveError('Inactive user passed to provision tenant')

    if hasattr(settings, 'TENANT_SUBFOLDER_PREFIX'):
        tenant_domain = tenant_slug
    else:
        tenant_domain = '{0}.{1}'.format(tenant_slug, settings.TENANT_USERS_DOMAIN)

    DomainModel = get_tenant_domain_model()
    if DomainModel.objects.filter(domain=tenant_domain).exists():
        raise ExistsError('Tenant URL already exists.')

    time_string = str(int(time.time()))
    # Must be valid postgres schema characters see:
    # https://www.postgresql.org/docs/9.2/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    # We generate unique schema names each time so we can keep tenants around
    # without taking up url/schema namespace.
    schema_name = '{0}_{1}'.format(tenant_slug, time_string)
    domain = None

    # noinspection PyBroadException
    try:
        # Wrap it in public schema context so schema consistency is maintained
        # if any error occurs
        with schema_context(get_public_schema_name()):
            tenant = TenantModel.objects.create(
                name=tenant_name,
                slug=tenant_slug,
                schema_name=schema_name,
                owner=user,
            )

            # Add one or more domains for the tenant
            domain = get_tenant_domain_model().objects.create(
                domain=tenant_domain,
                tenant=tenant,
                is_primary=True,
            )
            # Add user as a superuser inside the tenant
            tenant.add_user(user, is_superuser=True, is_staff=is_staff)
    except:
        if domain is not None:
            domain.delete()
        if tenant is not None:
            # Flag is set to auto-drop the schema for the tenant
            tenant.delete(True)
        raise

    return tenant_domain
