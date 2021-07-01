import pytest

from tenant_users.tenants import tasks
from test_project.settings import TENANT_USERS_DOMAIN


@pytest.mark.django_db()
def test_provision_tenant(tenant_user_admin):
    """Tests tasks.provision_tenant() for correctness."""
    slug = 'sample'
    tenant_domain = tasks.provision_tenant(
        'Sample Tenant',
        slug,
        tenant_user_admin,
    )

    assert tenant_domain == '{0}.{1}'.format(slug, TENANT_USERS_DOMAIN)
