import pytest
from django_tenants.utils import (
    get_tenant_model,
    get_tenant_types,
)

from tenant_users.tenants import tasks
from tenant_users.tenants.models import SchemaError


@pytest.mark.django_db
@pytest.mark.usefixtures('tenant_type_settings', 'django_db_setup')
def test_provision_tenant_with_valid_tenant_type(tenant_user_admin):
    """Tests tasks.provision_tenant() with a valid tenant type."""

    TenantModel = get_tenant_model()
    slug = 'type'

    # Create a tenant with a valid tenant type 'type2'
    tenant_domain = tasks.provision_tenant(
        'Sample Tenant type', slug, tenant_user_admin, tenant_type="type2"
    )
    tenant = TenantModel.objects.get(slug=slug)

    # Check if the tenant type matches the expected value
    assert tenant.type == "type2"


@pytest.mark.django_db
@pytest.mark.usefixtures('tenant_type_settings', 'django_db_setup')
def test_provision_tenant_with_invalid_tenant_type(tenant_user_admin):
    """Tests tasks.provision_tenant() with an invalid tenant type."""

    # Attempt to create a tenant with an invalid tenant type 'invalid_type'
    with pytest.raises(SchemaError) as excinfo:
        valid_tenant_types = get_tenant_types()
        valid_type_str = ", ".join(valid_tenant_types)
        invalid_tenant_type = "invalid_type"
        tenant_domain = tasks.provision_tenant(
            'Invalid Tenant type',
            "invalid",
            tenant_user_admin,
            tenant_type=invalid_tenant_type,
        )

    # Check if the correct exception message is raised
    assert str(
        excinfo.value
    ) == "{} is not a valid tenant type. Choices are {}.".format(
        invalid_tenant_type, ", ".join(valid_tenant_types)
    )
