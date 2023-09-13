from typing import List
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError, connection
from django_tenants.utils import get_tenant_model

from tenant_users.tenants.models import ExistsError, InactiveError
from tenant_users.tenants.tasks import provision_tenant

#: Constants
TenantModel = get_tenant_model()
TenantUser = get_user_model()


def list_schemas() -> List[str]:
    """
    Retrieve a list of all schemas present in the PostgreSQL database.

    This function queries the database's information schema to fetch the names of all
    existing schemas.

    Returns:
        list[str]: A list of schema names.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = [row[0] for row in cursor.fetchall()]
    return schemas


def test_provision_tenant(tenant_user_admin) -> None:
    """Tests provision_tenant() for correctness."""
    slug = 'sample'
    tenant_domain = provision_tenant(
        'Sample Tenant',
        slug,
        tenant_user_admin,
    )

    assert tenant_domain == '{0}.{1}'.format(slug, settings.TENANT_USERS_DOMAIN)


def test_provision_tenant_with_subfolder(settings, tenant_user_admin) -> None:
    """Tests provision_tenant() for correctness when using subfolders."""
    settings.TENANT_SUBFOLDER_PREFIX = 'clients'
    slug = 'sample'
    tenant_domain = provision_tenant(
        'Sample Tenant',
        slug,
        tenant_user_admin,
    )

    assert tenant_domain == slug


def test_provision_tenant_inactive_user(tenant_user) -> None:
    """Test tenant creation with inactive user."""
    tenant_user.is_active = False
    tenant_user.save()

    with pytest.raises(InactiveError, match='Inactive user passed'):
        provision_tenant(
            'inactive_test',
            'inactive_test',
            tenant_user.email,
        )


def test_duplicate_tenant_url(test_tenants, tenant_user) -> None:
    """Tests duplicate URL error."""
    # Get first non-public tenant to use
    slug = test_tenants.first().slug

    with pytest.raises(ExistsError, match='URL already exists'):
        provision_tenant(slug, slug, tenant_user.email)


def test_provision_with_schema_name(tenant_user) -> None:
    """
    Test tenant provisioning with a custom schema name.

    This test verifies that the `provision_tenant` function correctly creates a tenant
    with a custom schema name and that the corresponding schema is created in the database.
    """
    slug = 'sample'
    custom_schema_name = 'my_custom_name'
    provision_tenant(
        'Sample Tenant',
        slug,
        tenant_user.email,
        schema_name=custom_schema_name,
    )

    assert TenantModel.objects.get(schema_name=custom_schema_name)

    # Ensure the actual schema created in PostgreSQL is correct
    assert custom_schema_name in list_schemas()


def test_provision_tenant_tenant_creation_exception(tenant_user) -> None:
    """
    Test exception handling during tenant creation.

    This test ensures that the `provision_tenant` function raises the appropriate
    exception when there's a database error during tenant creation.
    """
    with patch(
        "django_test_app.companies.models.Company.objects.create",
        side_effect=DatabaseError("Database error"),
    ):
        with pytest.raises(Exception, match="Database error"):
            provision_tenant("Test Tenant", "test-tenant", tenant_user.email)


def test_provision_tenant_domain_creation_exception(tenant_user) -> None:
    """
    Test exception handling during domain creation for a tenant.

    This test ensures that the `provision_tenant` function raises the appropriate
    exception when there's a database error during domain creation and that any
    partial data (like schemas) is cleaned up.
    """
    slug = "test-tenant"

    schemas = list_schemas()

    with patch(
        "django_test_app.companies.models.Domain.objects.create",
        side_effect=DatabaseError("Domain error"),
    ):
        with pytest.raises(Exception, match="Domain error"):
            provision_tenant("Test Tenant", slug, tenant_user.email)

    # Ensure tenant was cleaned up
    assert not TenantModel.objects.filter(slug=slug).exists()

    # Double ensure no schema was left behind
    assert len(schemas) == len(list_schemas())


def test_provision_tenant_user_add_exception(tenant_user: TenantUser) -> None:
    """
    Test exception handling when adding a user to a tenant.

    This test ensures that the `provision_tenant` function raises the appropriate
    exception when there's an error adding a user to a tenant.
    """
    slug = "test-tenant"

    with patch(
        "django_test_app.companies.models.Company.add_user",
        side_effect=InactiveError("Exception error"),
    ):
        with pytest.raises(Exception, match="Exception error"):
            provision_tenant("Test Tenant", slug, tenant_user.email)

    # Ensure user wasn't added to a tenant
    assert tenant_user.tenants.count() == 1
