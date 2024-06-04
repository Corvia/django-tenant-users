"""This module is used to interact with the Database during tests.

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
PUBLIC_TENANT_OWNER_EMAIL = "owner@public.com"
PROVISION_TENANT_OWNER_EMAIL = "owner@provision.com"


@pytest.fixture(autouse=True)
def _common_db_setup(db, request):  # noqa: ARG001
    if request.node.get_closest_marker(name="no_db_setup"):
        return  # Skip the rest of the fixture for tests marked with 'no_db_setup'

    # Automatically stand up a public tenant for the majority of our tests
    create_public_tenant("public.test.com", PUBLIC_TENANT_OWNER_EMAIL)

    public_tenant = TenantModel.objects.get(
        schema_name=get_public_schema_name(),
    )
    connection.set_tenant(public_tenant)


@pytest.fixture()
def test_tenants(db, create_tenant):  # noqa: ARG001
    """Provision a few tenants for testing."""
    tenant_user = TenantUser.objects.create_user(
        email=PROVISION_TENANT_OWNER_EMAIL, password="123456"
    )
    for tenant_slug in ("one", "two"):
        create_tenant(tenant_user, tenant_slug)

    return TenantModel.objects.exclude(schema_name="public")


@pytest.fixture()
def create_tenant():
    """Create tenant helper fixture."""

    def create_tenant_function(
        tenant_user,
        tenant_slug,
        *,
        is_staff=False,
    ):
        """Handle provisioning of a new tenant."""
        tenant, _ = provision_tenant(
            tenant_slug, tenant_slug, tenant_user, is_staff=is_staff
        )
        return tenant

    return create_tenant_function
