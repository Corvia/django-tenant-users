import re
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django_tenants.utils import (
    get_multi_type_database_field_name,
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    get_tenant_types,
    has_multi_type_tenants,
    schema_context,
)

from tenant_users.tenants.models import ExistsError, InactiveError, SchemaError


@transaction.atomic()
def provision_tenant(
    tenant_name,
    tenant_slug,
    user_email,
    is_staff=False,
    is_superuser=True,
    tenant_type=None,
    schema_name=None,
    tenant_extra_data={},
):
    """Creates a tenant with default roles and permissions.

    This function creates a new tenant record, creates a user record for the tenant administrator, grants the user the default roles for the tenant, and provisions the tenant's infrastructure.

    **Args**

    * `tenant_name`: The name of the tenant.
    * `tenant_slug`: A unique identifier (slug) for the tenant.Used to create schema_name
    * `user_email`: The email address of the user who owns the tenant. Has to exist beforhand.
    * `tenant_type`: The type or category of the tenant.Defaults to 'None'.Used only when `HAS_MULTI_TYPE_TENANTS = True`
    * `schema_name`: Defaults to `f"{0}_{1}".format(tenant_slug, time_string)`
    * `is_staff`: Whether the user is  allowed to enter the admin panel. Defaults to `False`.
    * `is_superuser`:Whether the user has all permissions in the respective tenant. Defaults to `True`.
    * `tenant_extra_data`: Additional attributes for the tenant model (e.g., paid_until, on_trial,location,vision e.t.c).

    **Returns:**

    * `str`: The Fully Qualified Domain Name (FQDN) for the newly provisioned tenant.

    **Raises:**

    * `InactiveError`: If the user passed to the function is inactive.
    * `ExistsError`: If the tenant URL already exists.
    * `SchemaError`: If the tenant type is not valid."""

    tenant = None

    UserModel = get_user_model()
    TenantModel = get_tenant_model()

    user = UserModel.objects.get(email=user_email)
    if not user.is_active:
        raise InactiveError("Inactive user passed to provision tenant")

    if hasattr(settings, "TENANT_SUBFOLDER_PREFIX"):
        tenant_domain = tenant_slug
    else:
        tenant_domain = "{0}.{1}".format(tenant_slug, settings.TENANT_USERS_DOMAIN)

    DomainModel = get_tenant_domain_model()
    if DomainModel.objects.filter(domain=tenant_domain).exists():
        raise ExistsError("Tenant URL already exists.")
    if not schema_name:
        time_string = str(int(time.time()))
        # Must be valid postgres schema characters see:
        # https://www.postgresql.org/docs/9.2/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        # We generate unique schema names each time so we can keep tenants around
        # without taking up url/schema namespace.
        schema_name = "{0}_{1}".format(tenant_slug, time_string)

    # Validate tenant type if multi-tenants are enabled
    if has_multi_type_tenants():
        valid_tenant_types = get_tenant_types()

        if tenant_type not in valid_tenant_types:
            valid_type_str = ", ".join(valid_tenant_types)
            error_message = "{} is not a valid tenant type. Choices are {}.".format(
                tenant_type, valid_type_str
            )
            raise SchemaError(error_message)

        tenant_extra_data.update({get_multi_type_database_field_name(): tenant_type})

    # Attempt to create the tenant and domain within the schema context
    with schema_context(get_public_schema_name()):
        # Create a new tenant instance with provided data
        try:
            tenant = TenantModel.objects.create(
                name=tenant_name,
                slug=tenant_slug,
                schema_name=schema_name,
                owner=user,
                **tenant_extra_data,
            )

            # Add one or more domains for the tenant
            domain = get_tenant_domain_model().objects.create(
                domain=tenant_domain,
                tenant=tenant,
                is_primary=True,
            )
            # Add user as a superuser inside the tenant
            tenant.add_user(user, is_superuser=is_superuser, is_staff=is_staff)
    except:
        if domain is not None:
            domain.delete()
        if tenant is not None:
            # Flag is set to auto-drop the schema for the tenant
            tenant.delete(True)
        raise

    return tenant_domain
