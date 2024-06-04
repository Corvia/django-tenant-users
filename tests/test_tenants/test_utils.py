from unittest.mock import patch

import pytest
from django.conf import settings
from django_tenants.utils import get_public_schema_name, schema_context

from django_test_app.companies.models import Company, Domain
from django_test_app.users.models import TenantUser
from tenant_users.tenants import utils
from tenant_users.tenants.models import ExistsError, SchemaError


def test_get_current_tenant(public_tenant, test_tenants):
    """Tests utils.get_current_tenant() for correctness."""
    with schema_context(get_public_schema_name()):
        tenant = utils.get_current_tenant()
        assert tenant == public_tenant

    tenant = test_tenants.first()

    with schema_context(tenant.schema_name):
        current_tenant = utils.get_current_tenant()
        assert current_tenant == tenant


def test_duplicate_tenant_url(tenant_user):
    """Tests duplicate public tenant error."""
    with pytest.raises(ExistsError, match="Public tenant already exists"):
        utils.create_public_tenant("domain.com", tenant_user.email)


@pytest.mark.django_db()
@pytest.mark.no_db_setup()
def test_create_public_tenant():
    """Ensures correctness of create_public_tenant() function."""
    email = "user@domain.com"
    domain = "domain.test"

    # Create public tenant with basic params
    utils.create_public_tenant(domain, email)

    # Ensure expected objects all exist
    assert Domain.objects.filter(domain=domain).exists()
    assert Company.objects.filter(schema_name=get_public_schema_name()).exists()

    # Ensure user doesn't have a usable password
    user = TenantUser.objects.get(email=email)
    assert not user.has_usable_password()


@pytest.mark.django_db()
@pytest.mark.no_db_setup()
def test_create_public_tenant_with_specified_password():
    """Ensure password is set correct when specified during public tenant creation."""
    email = "user@domain.com"
    secret = "super_secure_123"  # noqa: S105
    utils.create_public_tenant("domain.test", email, password=secret)

    user = TenantUser.objects.get(email=email)
    assert user.tenants.filter(schema_name="public").exists()

    # Ensure the user is able to use the specified password
    assert user.check_password(secret)


@patch("django_test_app.companies.models.Company.objects.create")
@pytest.mark.usefixtures("_tenant_type_settings")
@pytest.mark.django_db()
@pytest.mark.no_db_setup()
def test_tenant_public_tenant_with_multitype(mock_create):
    """Tests that multi-type information is used during the Public Tenant creation."""
    # Since we're mocking, we expect an exception to be thrown after Tenant.create()
    with pytest.raises(ValueError, match='must be a "Company" instance'):
        utils.create_public_tenant("domain.test", "user@domain.com")

    # Check the mock was called
    assert mock_create.called

    # Get the arguments it was called with
    _, kwargs = mock_create.call_args

    # Ensure the multi-type database field was added during Tenant creation
    assert kwargs.get(settings.MULTI_TYPE_DATABASE_FIELD) == get_public_schema_name()


@pytest.mark.django_db()
@pytest.mark.no_db_setup()
def test_tenant_public_tenant_with_multitype_missing_public(settings):
    """Tests that multi-type information is used during the Public Tenant creation."""
    # Create invalid multitype configuration
    settings.HAS_MULTI_TYPE_TENANTS = True
    settings.TENANT_TYPES = {}

    public_name = get_public_schema_name()
    # Ensure we get a SchemaError back
    with pytest.raises(
        SchemaError,
        match=f"Please define a '{public_name}' tenant type.",
    ):
        utils.create_public_tenant("domain.test", "user@domain.com")


@pytest.mark.django_db()
@pytest.mark.no_db_setup()
def test_create_public_tenant_with_tenant_extras():
    """Ensures correctness of create_public_tenant() function."""
    email = "user@domain.com"
    domain = "domain.test"
    extra_data = "extra data added"

    # Create public tenant with tenant_extra_data
    public_tenant, _, _ = utils.create_public_tenant(
        domain, email, tenant_extra_data={"type": extra_data}
    )
    assert public_tenant.type == extra_data
    # Test deleting tenant
    with pytest.raises(ValueError, match="Cannot delete public tenant schema"):
        public_tenant.delete_tenant()
