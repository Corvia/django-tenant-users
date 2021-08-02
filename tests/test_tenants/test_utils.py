import pytest

from tenant_users import compat
from tenant_users.tenants import utils
from tenant_users.tenants.models import ExistsError


@pytest.mark.django_db()
def test_get_current_tenant(public_tenant, test_tenants):
    """Tests utils.get_current_tenant() for correctness."""
    with compat.schema_context(compat.get_public_schema_name()):
        tenant = utils.get_current_tenant()
        assert tenant == public_tenant

    tenant = test_tenants.first()

    with compat.schema_context(tenant.schema_name):
        current_tenant = utils.get_current_tenant()
        assert current_tenant == tenant


@pytest.mark.django_db()
def test_duplicate_tenant_url(tenant_user):
    """Tests duplicate public tenant error."""
    with pytest.raises(ExistsError, match='Public tenant already exists'):
        utils.create_public_tenant('domain.com', tenant_user.email)


@pytest.mark.django_db()
def test_fix_tenant_urls(public_tenant, test_tenants):
    """
    Tests utils.fix_tenant_url() for correctness.

    This utility function is only applicable to django-tenant-schemas.
    """
    new_domain = 'new-pytest-domain.com'

    if compat.TENANT_SCHEMAS:
        utils.fix_tenant_urls(new_domain)
        public_tenant.refresh_from_db()

        assert new_domain == public_tenant.domain_url
        assert new_domain in test_tenants.first().domain_url
    else:
        pytest.skip('Not supported for django-tenants')
