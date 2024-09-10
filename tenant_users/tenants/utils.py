from typing import Optional

from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import (
    get_multi_type_database_field_name,
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    get_tenant_types,
    has_multi_type_tenants,
)

from tenant_users.tenants.models import ExistsError, SchemaError


def get_current_tenant():
    """
    Retrieves the current tenant based on the current database schema.

    This function gets the current schema name from the database connection,
    retrieves the tenant model, and then fetches the tenant instance that
    matches the current schema name.

    Returns:
        tenant: The tenant instance corresponding to the current database schema.

    """
    current_schema = connection.schema_name
    TenantModel = get_tenant_model()  # noqa: N806
    tenant = TenantModel.objects.get(schema_name=current_schema)
    return tenant


def create_public_tenant(
    domain_url,
    owner_email,
    *,
    is_superuser: bool = False,
    is_staff: bool = False,
    tenant_extra_data: Optional[dict] = None,
    verbosity=1,
    **owner_extra,
):
    """Creates a public tenant and assigns an owner user.

    This function sets up a new public tenant in a multi-tenant Django application. It assigns an
    owner user to the tenant, with the option to specify additional user and tenant attributes.

    Args:
        domain_url (str): The URL for the public tenant's domain.
        owner_email (str): Email address of the owner user.
        is_superuser (bool): If True, the owner has superuser privileges. Defaults to False.
        is_staff (bool): If True, the owner has staff access. Defaults to False.
        tenant_extra_data (dict, optional): Additional data for the tenant model.
        **owner_extra: Arbitrary keyword arguments for additional owner user attributes.

    Returns:
        tuple: A tuple containing the tenant object, domain object, and user object.
    """
    if tenant_extra_data is None:
        tenant_extra_data = {}

    UserModel = get_user_model()  # noqa: N806
    TenantModel = get_tenant_model()  # noqa: N806
    public_schema_name = get_public_schema_name()

    if TenantModel.objects.filter(schema_name=public_schema_name).first():
        raise ExistsError("Public tenant already exists")

    # Create public tenant user. This user doesn't go through object manager
    # create_user function because public tenant does not exist yet
    profile = UserModel.objects.create(
        email=owner_email,
        is_active=True,
        **owner_extra,
    )

    # Create the public tenant
    if has_multi_type_tenants():
        valid_tenant_types = get_tenant_types()

        # Check if the Public tenant type is defined
        if public_schema_name not in valid_tenant_types:
            error_message = f"Please define a '{public_schema_name}' tenant type."
            raise SchemaError(error_message)

        tenant_extra_data.update(
            {get_multi_type_database_field_name(): public_schema_name}
        )

    public_tenant = TenantModel(
        schema_name=public_schema_name,
        name="Public Tenant",
        owner=profile,
        **tenant_extra_data,
    )

    public_tenant.save(verbosity=verbosity)

    # Add one or more domains for the tenant
    domain = get_tenant_domain_model().objects.create(
        domain=domain_url,
        tenant=public_tenant,
        is_primary=True,
    )

    # Add system user to public tenant (no permissions)
    public_tenant.add_user(profile, is_superuser=is_superuser, is_staff=is_staff)

    # Handle setting the password for the user
    if "password" in owner_extra:
        profile.set_password(owner_extra["password"])
    else:
        profile.set_unusable_password()
    profile.save(update_fields=["password"])

    return public_tenant, domain, profile
