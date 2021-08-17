from django.contrib.auth import get_user_model
from django.db import connection

from tenant_users.compat import (
    TENANT_SCHEMAS,
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
)
from tenant_users.tenants.models import ExistsError


def get_current_tenant():
    current_schema = connection.schema_name
    TenantModel = get_tenant_model()
    tenant = TenantModel.objects.get(schema_name=current_schema)
    return tenant


def create_public_tenant(domain_url, owner_email, **owner_extra):
    UserModel = get_user_model()
    TenantModel = get_tenant_model()
    public_schema_name = get_public_schema_name()

    if TenantModel.objects.filter(schema_name=public_schema_name).first():
        raise ExistsError('Public tenant already exists')

    # Create public tenant user. This user doesn't go through object manager
    # create_user function because public tenant does not exist yet
    profile = UserModel.objects.create(
        email=owner_email,
        is_active=True,
        **owner_extra,
    )
    profile.set_unusable_password()
    profile.save()

    # Create public tenant

    if TENANT_SCHEMAS:
        public_tenant = TenantModel.objects.create(
            domain_url=domain_url,
            schema_name=public_schema_name,
            name='Public Tenant',
            owner=profile,
        )
    else:
        public_tenant = TenantModel.objects.create(
            schema_name=public_schema_name,
            name='Public Tenant',
            owner=profile,
        )

        # Add one or more domains for the tenant
        get_tenant_domain_model().objects.create(
            domain=domain_url,
            tenant=public_tenant,
            is_primary=True,
        )

    # Add system user to public tenant (no permissions)
    public_tenant.add_user(profile)


def fix_tenant_urls(domain_url):
    """
    Helper function to update the domain urls on all tenants
    Useful for domain changes in development
    """
    TenantModel = get_tenant_model()
    public_schema_name = get_public_schema_name()

    tenants = TenantModel.objects.all()
    for tenant in tenants:
        if tenant.schema_name == public_schema_name:
            tenant.domain_url = domain_url
        else:
            # Assume the URL is wrong, parse out the subdomain
            # and glue it back to the domain URL configured
            slug = tenant.domain_url.split('.')[0]
            new_url = '{0}.{1}'.format(slug, domain_url)
            tenant.domain_url = new_url
        tenant.save()
