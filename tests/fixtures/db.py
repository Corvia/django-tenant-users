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
TEST_TENANT_NAME = 'pytest'
TEST_USER_EMAIL = 'primary-user@test.com'


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: PT004
    """Override the database setup to ensure proper setup."""
    with django_db_blocker.unblock():
        _provision_public_tenant()

        public_tenant = TenantModel.objects.get(
            schema_name=get_public_schema_name(),
        )
        connection.set_tenant(public_tenant)


def _provision_public_tenant():
    """Handle public tenant schema."""
    schema_name = get_public_schema_name()

    try:
        TenantModel.objects.get(schema_name=schema_name)
    except TenantModel.DoesNotExist:
        create_public_tenant('public.test.com', TEST_USER_EMAIL)


@pytest.fixture()
def test_tenants(db, create_tenant):  # noqa: PT004
    """Provision a few tenants for testing."""
    tenant_user = TenantUser.objects.get(email=TEST_USER_EMAIL)
    for tenant_slug in ('one', 'two'):
        create_tenant(tenant_user, tenant_slug)

    return TenantModel.objects.exclude(schema_name='public')


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
