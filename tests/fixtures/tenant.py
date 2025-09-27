import pytest
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, schema_context

from django_test_app.users.models import GuidUser

#: Constants
TenantModel = get_tenant_model()
TenantUser = get_user_model()
_USER_PASS = "test1234"  # noqa: S105


@pytest.fixture
def guid_tenant_user(db) -> GuidUser:
    with schema_context("public"):
        return TenantUser.objects.create_user(email="guid-user@test.com")


@pytest.fixture
def public_tenant(db) -> TenantModel:
    """Returns Public Tenant instance."""
    return TenantModel.objects.get(schema_name="public")


@pytest.fixture
def tenant_user_admin(db) -> TenantUser:
    """Returns Admin User instance."""
    with schema_context("public"):
        return TenantUser.objects.create_superuser(
            _USER_PASS,
            email="super@user.com",
        )


@pytest.fixture
def tenant_user(db) -> TenantUser:
    """Returns Admin User instance."""
    with schema_context("public"):
        return TenantUser.objects.create_user(email="tenant-user@test.com")
