"""
This module is used to interact with the Database during tests.

https://pytest-django.readthedocs.io/en/latest/database.html
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_public_schema_name, get_tenant_model

from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant

#: Constants
TenantModel = get_tenant_model()
TenantUser = get_user_model()
TEST_TENANT_NAME = "pytest"
TEST_USER_EMAIL = "primary-user@test.com"


@pytest.fixture(autouse=True)
def common_db_setup(db, request):
    if request.node.get_closest_marker(name="no_db_setup"):
        return  # Skip the rest of the fixture for tests marked with 'no_db_setup'

    # Automatically stand up a public tenant for the majority of our tests
    create_public_tenant("public.test.com", TEST_USER_EMAIL)

    public_tenant = TenantModel.objects.get(
        schema_name=get_public_schema_name(),
    )
    connection.set_tenant(public_tenant)


@pytest.fixture()
def test_tenants(db, create_tenant):  # noqa: PT004
    """Provision a few tenants for testing."""
    tenant_user = TenantUser.objects.get(email=TEST_USER_EMAIL)
    for tenant_slug in ("one", "two"):
        create_tenant(tenant_user, tenant_slug)

    return TenantModel.objects.exclude(schema_name="public")


@pytest.fixture()
def create_tenant():
    """Create tenant helper fixture."""

    def create_tenant_function(  # noqa: WPS430
        tenant_user,
        tenant_slug,
        is_staff=False,
    ):
        """Handle provisioning of a new tenant."""
        provision_tenant(tenant_slug, tenant_slug, tenant_user.email, is_staff)
        tenant = TenantModel.objects.get(slug=tenant_slug)
        return tenant

    return create_tenant_function
