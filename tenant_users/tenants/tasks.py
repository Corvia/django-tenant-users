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
def provision_tenant(  # noqa: PLR0913
    tenant_name,
    tenant_slug,
    user_email,
    *,
    is_staff: bool = False,
    is_superuser: bool = True,
    tenant_type=None,
    schema_name=None,
    tenant_extra_data=None,
):
    """Creates and initializes a new tenant with specified attributes and default roles.

    Args:
        tenant_name (str): The name of the tenant.
        tenant_slug (str): A unique slug for the tenant. It's used to create the schema_name.
        user_email (str): Email address of the tenant's owner. The user must exist beforehand.
        is_staff (bool, optional): If True, the user has staff access. Defaults to False.
        is_superuser (bool, optional): If True, the user has all permissions. Defaults to True.
        tenant_type (str, optional): Type of the tenant, used with `HAS_MULTI_TYPE_TENANTS = True`.
        schema_name (str, optional): The schema name for the tenant. Defaults to a combination of the slug and a timestamp.
        tenant_extra_data (dict, optional): Additional data for the tenant model.

    Returns:
        str: The Fully Qualified Domain Name (FQDN) for the newly provisioned tenant.

    Raises:
        InactiveError: If the user is inactive.
        ExistsError: If the tenant URL already exists.
        SchemaError: If the tenant type is not valid.
    """
    tenant = None

    if tenant_extra_data is None:
        tenant_extra_data = {}

    UserModel = get_user_model()  # noqa: N806
    TenantModel = get_tenant_model()  # noqa: N806

    user = UserModel.objects.get(email=user_email)
    if not user.is_active:
        raise InactiveError("Inactive user passed to provision tenant")

    if hasattr(settings, "TENANT_SUBFOLDER_PREFIX"):
        tenant_domain = tenant_slug
    else:
        tenant_domain = f"{tenant_slug}.{settings.TENANT_USERS_DOMAIN}"

    DomainModel = get_tenant_domain_model()  # noqa: N806
    if DomainModel.objects.filter(domain=tenant_domain).exists():
        raise ExistsError("Tenant URL already exists.")
    if not schema_name:
        time_string = str(int(time.time()))
        # Must be valid postgres schema characters see:
        # https://www.postgresql.org/docs/9.2/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        # We generate unique schema names each time so we can keep tenants around
        # without taking up url/schema namespace.
        schema_name = f"{tenant_slug}_{time_string}"

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
        tenant = TenantModel.objects.create(
            name=tenant_name,
            slug=tenant_slug,
            schema_name=schema_name,
            owner=user,
            **tenant_extra_data,
        )

        # Create a domain associated with the tenant and mark as primary
        domain_model = get_tenant_domain_model()
        domain_model.objects.create(
            domain=tenant_domain, tenant=tenant, is_primary=True
        )

        # Add the user to the tenant with provided roles
        tenant.add_user(user, is_superuser=is_superuser, is_staff=is_staff)

    # Return the domain associated with the tenant
    return tenant_domain
