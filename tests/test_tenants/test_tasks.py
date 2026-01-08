from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import DatabaseError, connection

from django_test_app.companies.models import Company
from tenant_users.constants import INACTIVE_USER_ERROR_MESSAGE
from tenant_users.tenants.models import ExistsError, InactiveError, SchemaError
from tenant_users.tenants.tasks import provision_tenant

if TYPE_CHECKING:
    from django_test_app.users.models import TenantUser


def list_schemas() -> list[str]:
    """Retrieve a list of all schemas present in the PostgreSQL database.

    This function queries the database's information schema to fetch the names of all
    existing schemas.

    Returns:
        list[str]: A list of schema names.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        return [row[0] for row in cursor.fetchall()]


def test_provision_tenant(tenant_user_admin) -> None:
    """Tests provision_tenant() for correctness."""
    slug = "sample"
    tenant_name = "Sample Tenant"
    tenant, domain = provision_tenant(
        tenant_name,
        slug,
        tenant_user_admin,
    )
    assert tenant.name == tenant_name
    assert tenant.owner == tenant_user_admin
    assert domain.domain == f"{slug}.{settings.TENANT_USERS_DOMAIN}"


def test_provision_tenant_with_subfolder(settings, tenant_user_admin) -> None:
    """Tests provision_tenant() for correctness when using subfolders."""
    settings.TENANT_SUBFOLDER_PREFIX = "clients"
    slug = "sample"
    tenant_name = "Sample Tenant"
    tenant, domain = provision_tenant(
        tenant_name,
        slug,
        tenant_user_admin,
    )
    assert tenant.name == tenant_name
    assert tenant.owner == tenant_user_admin

    assert domain.domain == slug


def test_provision_tenant_inactive_user(tenant_user) -> None:
    """Test tenant creation with inactive user."""
    tenant_user.is_active = False
    tenant_user.save(update_fields=["is_active"])

    with pytest.raises(InactiveError, match=INACTIVE_USER_ERROR_MESSAGE):
        provision_tenant(
            "inactive_test",
            "inactive_test",
            tenant_user,
        )


def test_duplicate_tenant_url(test_tenants, tenant_user) -> None:
    """Tests duplicate URL error."""
    # Get first non-public tenant to use
    slug = test_tenants.first().slug

    with pytest.raises(ExistsError, match="URL already exists"):
        provision_tenant(slug, slug, tenant_user)


def test_provision_tenant_domain_extra_data_is_used(tenant_user_admin) -> None:
    """Ensures domain_extra_data is passed through to domain creation."""
    slug = "sample-domain-extra"
    tenant_name = "Sample Tenant"

    tenant, domain = provision_tenant(
        tenant_name,
        slug,
        tenant_user_admin,
        domain_extra_data={"notes": "hello"},
    )

    assert domain.tenant == tenant
    assert domain.domain == f"{slug}.{settings.TENANT_USERS_DOMAIN}"
    assert domain.notes == "hello"


def test_provision_tenant_default_roles_passed_to_add_user(tenant_user_admin) -> None:
    """Ensures add_user() is called with default role flags."""
    slug = "sample-default-roles"
    tenant_name = "Sample Tenant"

    with patch("django_test_app.companies.models.Company.add_user") as add_user_mock:
        provision_tenant(tenant_name, slug, tenant_user_admin)

    add_user_mock.assert_called_once()
    args, kwargs = add_user_mock.call_args
    assert args[0] == tenant_user_admin
    assert kwargs == {"is_superuser": True, "is_staff": False}


def test_provision_tenant_tenant_creation_exception(tenant_user) -> None:
    """Test exception handling during tenant creation.

    This test ensures that the `provision_tenant` function raises the appropriate
    exception when there's a database error during tenant creation.
    """
    with (
        patch(
            "django_test_app.companies.models.Company.objects.create",
            side_effect=DatabaseError("Database error"),
        ),
        pytest.raises(Exception, match="Database error"),
    ):
        provision_tenant("Test Tenant", "test-tenant", tenant_user)


def test_provision_tenant_domain_creation_exception(tenant_user) -> None:
    """Test exception handling during domain creation for a tenant.

    This test ensures that the `provision_tenant` function raises the appropriate
    exception when there's a database error during domain creation and that any
    partial data (like schemas) is cleaned up.
    """
    slug = "test-tenant"

    schemas = list_schemas()

    with (
        patch(
            "django_test_app.companies.models.Domain.objects.create",
            side_effect=DatabaseError("Domain error"),
        ),
        pytest.raises(Exception, match="Domain error"),
    ):
        provision_tenant("Test Tenant", slug, tenant_user)

    # Ensure tenant was cleaned up
    assert not Company.objects.filter(slug=slug).exists()

    # Double ensure no schema was left behind
    assert len(schemas) == len(list_schemas())


def test_provision_tenant_domain_extra_data_invalid_is_atomic(tenant_user) -> None:
    """Ensures atomic rollback when domain_extra_data contains invalid fields."""
    slug = "bad-domain-extra"
    schemas = list_schemas()

    with pytest.raises(TypeError):
        provision_tenant(
            "Test Tenant",
            slug,
            tenant_user,
            domain_extra_data={"does_not_exist": "boom"},
        )

    assert not Company.objects.filter(slug=slug).exists()
    assert len(schemas) == len(list_schemas())


def test_provision_tenant_user_add_exception(tenant_user: TenantUser) -> None:
    """Test exception handling when adding a user to a tenant.

    This test ensures that the `provision_tenant` function raises the appropriate
    exception when there's an error adding a user to a tenant.
    """
    slug = "test-tenant"
    schemas = list_schemas()

    with (
        patch(
            "django_test_app.companies.models.Company.add_user",
            side_effect=InactiveError("Exception error"),
        ),
        pytest.raises(Exception, match="Exception error"),
    ):
        provision_tenant("Test Tenant", slug, tenant_user)

    # Ensure user wasn't added to a tenant
    assert tenant_user.tenants.count() == 1
    # Ensure tenant + schema weren't persisted
    assert not Company.objects.filter(slug=slug).exists()
    assert len(schemas) == len(list_schemas())


@pytest.mark.usefixtures("_tenant_type_settings")
def test_provision_tenant_with_multitype_invalid_type_raises_schema_error(
    tenant_user_admin,
) -> None:
    """Ensures SchemaError is raised for invalid tenant_type when multitype enabled."""
    slug = "multi-invalid"

    with pytest.raises(SchemaError, match="not a valid tenant type"):
        provision_tenant(
            "Test Tenant",
            slug,
            tenant_user_admin,
            tenant_type="does-not-exist",
        )

    assert not Company.objects.filter(slug=slug).exists()


@pytest.mark.usefixtures("_tenant_type_settings")
def test_provision_tenant_with_multitype_sets_type_field(tenant_user_admin) -> None:
    """Ensures the multi-type database field is populated during tenant creation."""
    slug = "multi-valid"
    tenant, _ = provision_tenant(
        "Test Tenant",
        slug,
        tenant_user_admin,
        tenant_type="type2",
    )

    # MULTI_TYPE_DATABASE_FIELD is configured as "type" by the fixture
    assert tenant.type == "type2"


def test_provision_tenant_with_tenant_extras(tenant_user) -> None:
    """Test tenant provisioning with a custom schema name.

    This test verifies that the `provision_tenant` function correctly creates a tenant
    with a custom schema name and that the corresponding schema is created in the database.
    """
    slug = "sample"
    custom_schema_name = "my_custom_name"
    extra_data = "extra data added"
    tenant, _ = provision_tenant(
        tenant_name="Sample Tenant",
        tenant_slug=slug,
        owner=tenant_user,
        schema_name=custom_schema_name,
        tenant_extra_data={"type": extra_data},
    )

    assert tenant.type == extra_data
