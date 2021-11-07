import pytest
from django_tenants.utils import get_public_schema_name, schema_context

from tenant_users.tenants import utils
from tenant_users.tenants.models import ExistsError


@pytest.mark.django_db()
def test_get_current_tenant(public_tenant, test_tenants):
    """Tests utils.get_current_tenant() for correctness."""
    with schema_context(get_public_schema_name()):
        tenant = utils.get_current_tenant()
        assert tenant == public_tenant

    tenant = test_tenants.first()

    with schema_context(tenant.schema_name):
        current_tenant = utils.get_current_tenant()
        assert current_tenant == tenant


@pytest.mark.django_db()
def test_duplicate_tenant_url(tenant_user):
    """Tests duplicate public tenant error."""
    with pytest.raises(ExistsError, match='Public tenant already exists'):
        utils.create_public_tenant('domain.com', tenant_user.email)
