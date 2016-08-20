import time
from django.conf import settings
from django.contrib.auth import get_user_model
from tenant_schemas.utils import get_tenant_model

from .models import InactiveError, ExistsError
from ..permissions.roles import COMPANY_TENANT_DEFAULT_ROLES, COMPANY_ROLE_ADMIN

def provision_company(company_name, company_slug, user_email):
    """Create a company with default roles and permissions

    Returns:
    The FQDN for the company.
    """
    company = None

    UserModel = get_user_model()
    TenantModel = get_tenant_model()

    user = UserModel.objects.get(email=user_email)
    if not user.is_active:
        raise InactiveError("Inactive user passed to provision company")

    company_domain = '{}.{}'.format(company_slug, settings.TENANT_USERS_DOMAIN)

    if TenantModel.objects.filter(domain_url=company_domain).first():
        raise ExistsError("Company URL already exists")

    time_string = str(int(time.time()))
    # Must be valid postgres schema characters see:
    # https://www.postgresql.org/docs/9.2/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    # We generate unique schema names each time so we can keep companies around without
    # taking up url/schema namespace. 
    schema_name = '{}_{}'.format(company_slug, time_string)

    try:
        # Create a Company object and tenant schema
        company = TenantModel.objects.create(
            name=company_name,
            slug=company_slug,
            domain_url=company_domain, 
            schema_name=schema_name,
            owner = user,
        )

        if hasattr(settings, "COMPANY_TENANT_DEFAULT_ROLES"):
            default_roles = settings.COMPANY_TENANT_DEFAULT_ROLES
        else:
            default_roles = COMPANY_TENANT_DEFAULT_ROLES

        # Create the default roles and permissions inside the company
        company.create_roles(default_roles)

        # Set user to admin role on the company 
        company.assign_user_role(user, COMPANY_ROLE_ADMIN, True)
    except:
        if company is not None:
            #Flag is set to auto-drop the schema for the tenant
            company.delete(True)
        raise

    return company_domain
