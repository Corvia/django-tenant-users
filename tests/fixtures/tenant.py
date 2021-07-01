import pytest
from django.db import connection
from django_tenants.test.client import TenantClient
from django_tenants.utils import schema_context

from test_project.companies.models import Company
from test_project.users.models import TenantUser

_USER_PASS = 'test1234'  # noqa: S105


@pytest.fixture()
def public_tenant(db) -> Company:
    """Returns Public Tenant instance."""
    return Company.objects.get(schema_name='public')


@pytest.fixture()
def tenant_user_admin(db) -> TenantUser:
    """Returns Admin User instance."""
    with schema_context('public'):
        return TenantUser.objects.create_superuser(
            _USER_PASS,
            email='super@user.com',
        )
