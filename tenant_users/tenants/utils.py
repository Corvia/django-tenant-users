from __future__ import annotations

import warnings
from typing import Any

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django_tenants.utils import (
    get_multi_type_database_field_name,
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    get_tenant_types,
    has_multi_type_tenants,
)

from tenant_users.tenants.models import ExistsError, SchemaError, TenantBase

AnyTenant = TenantBase


def get_current_tenant() -> AnyTenant:
    """Retrieves the current tenant based on the current database schema.

    This function gets the current schema name from the database connection,
    retrieves the tenant model, and then fetches the tenant instance that
    matches the current schema name.

    Returns:
        tenant: The tenant instance corresponding to the current database schema.

    """
    current_schema = connection.schema_name  # type: ignore[attr-defined]
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=current_schema)


@transaction.atomic
def create_public_tenant(  # noqa: PLR0913
    domain_url,
    owner_email,
    *,
    is_superuser: bool = False,
    is_staff: bool = False,
    tenant_extra_data: dict[str, Any] | None = None,
    domain_extra_data: dict[str, Any] | None = None,
    owner_extra_data: dict[str, Any] | None = None,
    verbosity=1,
    **owner_extra: Any,
):
    """Creates a public tenant, assigns an owner user, and sets up the tenant's domain.

    This function sets up a new public tenant in a multi-tenant Django application. It assigns an
    owner user to the tenant, with the option to specify additional user and tenant attributes.

    Args:
        domain_url (str): The URL for the public tenant's domain.
        owner_email (str): Email address of the owner user.
        is_superuser (bool): If True, the owner has superuser privileges. Defaults to False.
        is_staff (bool): If True, the owner has staff access. Defaults to False.
        tenant_extra_data (dict, optional): Additional data for the tenant model.
        domain_extra_data (dict, optional): Additional data for the domain model.
        owner_extra_data (dict, optional): Additional data for the owner user.
        verbosity (int, optional): Verbosity level for saving the tenant. Defaults to 1.
        **owner_extra: Deprecated. Extra keyword arguments are treated as owner fields.
            Use owner_extra_data instead.

    Returns:
        tuple: A tuple containing the tenant object, domain object, and user object.
    """
    extra_data = {
        "tenant": tenant_extra_data or {},
        "domain": domain_extra_data or {},
        "owner": owner_extra_data or {},
    }

    if owner_extra:
        warnings.warn(
            "Passing extra keyword arguments to create_public_tenant() is deprecated. "
            "Use owner_extra_data={...} instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # preserve explicit owner_extra_data values over deprecated kwargs
        for key, value in owner_extra.items():
            extra_data["owner"].setdefault(key, value)

    UserModel = get_user_model()
    TenantModel = get_tenant_model()
    public_schema_name = get_public_schema_name()

    if TenantModel.objects.filter(schema_name=public_schema_name).first():
        raise ExistsError("Public tenant already exists")

    # Create public tenant user. This user doesn't go through object manager
    # create_user function because public tenant does not exist yet
    profile = UserModel.objects.create(
        email=owner_email,
        is_active=True,
        **extra_data["owner"],
    )

    # Create the public tenant
    if has_multi_type_tenants():
        valid_tenant_types = get_tenant_types()

        # Check if the Public tenant type is defined
        if public_schema_name not in valid_tenant_types:
            error_message = f"Please define a '{public_schema_name}' tenant type."
            raise SchemaError(error_message)

        extra_data["tenant"].update(
            {get_multi_type_database_field_name(): public_schema_name}
        )

    public_tenant = TenantModel(
        schema_name=public_schema_name,
        name="Public Tenant",
        owner=profile,
        **extra_data["tenant"],
    )

    public_tenant.save(verbosity=verbosity)

    # Add one or more domains for the tenant
    domain = get_tenant_domain_model().objects.create(
        domain=domain_url,
        tenant=public_tenant,
        is_primary=True,
        **extra_data["domain"],
    )

    # Add system user to public tenant (no permissions)
    public_tenant.add_user(profile, is_superuser=is_superuser, is_staff=is_staff)

    # Handle setting the password for the user
    if "password" in extra_data["owner"]:
        profile.set_password(extra_data["owner"]["password"])
    else:
        profile.set_unusable_password()
    profile.save(update_fields=["password"])

    return public_tenant, domain, profile
