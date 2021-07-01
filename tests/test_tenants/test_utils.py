import pytest
from django_tenants.utils import get_public_schema_name, schema_context

from tenant_users.tenants import utils


@pytest.mark.django_db()
def test_get_current_tenant(public_tenant):
    """Tests utils.get_current_tenant() for correctness."""
    with schema_context(get_public_schema_name()):
        tenant = utils.get_current_tenant()

        assert tenant == public_tenant
