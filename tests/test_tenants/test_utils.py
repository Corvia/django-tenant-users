from unittest.mock import Mock, patch

import pytest
from django.conf import settings
from django.db.models.query import QuerySet
from django_tenants.utils import get_public_schema_name, schema_context

from django_test_app.companies.models import Company, Domain
from django_test_app.users.models import TenantUser
from tenant_users.permissions.models import UserTenantPermissions
from tenant_users.tenants import utils
from tenant_users.tenants.models import ExistsError, SchemaError


def test_get_current_tenant(
    public_tenant: Company,
    test_tenants: QuerySet[Company],
) -> None:
    """Tests utils.get_current_tenant() for correctness."""
    with schema_context(get_public_schema_name()):
        tenant = utils.get_current_tenant()
        assert tenant == public_tenant

    other_tenant = test_tenants.first()
    assert other_tenant

    with schema_context(other_tenant.schema_name):
        current_tenant = utils.get_current_tenant()
        assert current_tenant == other_tenant


def test_duplicate_tenant_url(tenant_user):
    """Tests duplicate public tenant error."""
    with pytest.raises(ExistsError, match="Public tenant already exists"):
        utils.create_public_tenant("domain.com", tenant_user.email)


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant():
    """Ensures correctness of create_public_tenant() function."""
    email = "user@domain.com"
    domain = "domain.test"

    # Create public tenant with basic params
    public_tenant, created_domain, user = utils.create_public_tenant(domain, email)

    assert public_tenant.schema_name == get_public_schema_name()
    assert created_domain.tenant == public_tenant
    assert created_domain.domain == domain
    assert created_domain.is_primary
    assert public_tenant.owner == user

    # Ensure expected objects all exist
    assert Domain.objects.filter(domain=domain).exists()
    assert Company.objects.filter(schema_name=get_public_schema_name()).exists()

    # Ensure user doesn't have a usable password
    user = TenantUser.objects.get(email=email)
    assert not user.has_usable_password()


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_with_specified_password():
    """Ensure password is set correct when specified during public tenant creation."""
    email = "user@domain.com"
    secret = "super_secure_123"  # noqa: S105
    utils.create_public_tenant(
        "domain.test", email, owner_extra_data={"password": secret}
    )

    user = TenantUser.objects.get(email=email)
    assert user.tenants.filter(schema_name="public").exists()

    # Ensure the user is able to use the specified password
    assert user.check_password(secret)


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_domain_extra_data_is_used():
    """Ensures domain_extra_data is passed through to domain creation."""
    domain = "domain.test"

    _, created_domain, _ = utils.create_public_tenant(
        domain,
        "user@domain.com",
        domain_extra_data={"notes": "hello"},
    )

    created_domain.refresh_from_db()
    assert created_domain.domain == domain
    assert created_domain.notes == "hello"


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_owner_extra_data_is_used():
    """Ensures owner_extra_data is passed through to owner creation."""
    email = "user@domain.com"
    domain = "domain.test"
    owner_name = "Owner Name"

    _, _, user = utils.create_public_tenant(
        domain,
        email,
        owner_extra_data={"name": owner_name},
    )

    user.refresh_from_db()
    assert user.email == email
    assert user.name == owner_name
    assert user.is_active is True


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_deprecated_owner_extra_kwargs_warns_and_works():
    """Ensures legacy **owner_extra kwargs emit a warning and are applied."""
    email = "user-deprecated@domain.com"
    domain = "domain.test"

    with pytest.warns(DeprecationWarning, match=r"owner_extra_data"):
        _, _, user = utils.create_public_tenant(domain, email, name="Deprecated Name")

    user.refresh_from_db()
    assert user.email == email
    assert user.name == "Deprecated Name"


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_deprecated_kwargs_do_not_override_new_owner_extra_data():
    """Ensures explicit owner_extra_data wins over deprecated kwargs on conflicts."""
    email = "user-deprecated2@domain.com"
    domain = "domain.test"

    with pytest.warns(
        DeprecationWarning,
        match="extra keyword arguments to create_public_tenant\\(\\) is deprecated",
    ):
        _, _, user = utils.create_public_tenant(
            domain,
            email,
            owner_extra_data={"name": "Explicit new"},
            name="Deprecated",
        )

    user.refresh_from_db()
    assert user.name == "Explicit new"


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_owner_flags_create_correct_permissions():
    """Ensures is_staff/is_superuser are persisted via add_user()."""
    email = "user@domain.com"
    domain = "domain.test"

    public_tenant, _, profile = utils.create_public_tenant(
        domain,
        email,
        is_staff=True,
        is_superuser=True,
    )

    with schema_context(public_tenant.schema_name):
        perms = UserTenantPermissions.objects.get(profile=profile)
        assert perms.is_staff is True
        assert perms.is_superuser is True


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_is_atomic_on_domain_creation_error():
    """Ensures the transaction rolls back if domain creation fails."""
    email = "user@domain.com"
    domain = "domain.test"

    with pytest.raises(TypeError):
        utils.create_public_tenant(
            domain,
            email,
            domain_extra_data={"does_not_exist": "boom"},
        )

    # If atomic is working, nothing should have been persisted.
    assert not TenantUser.objects.filter(email=email).exists()
    assert not Company.objects.filter(schema_name=get_public_schema_name()).exists()
    assert not Domain.objects.filter(domain=domain).exists()


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_is_atomic_on_schema_error(settings):
    """Ensures the transaction rolls back if schema validation fails."""
    # Create invalid multitype configuration
    settings.HAS_MULTI_TYPE_TENANTS = True
    settings.TENANT_TYPES = {}

    email = "user@domain.com"
    domain = "domain.test"

    public_name = get_public_schema_name()
    with pytest.raises(
        SchemaError,
        match=f"Please define a '{public_name}' tenant type.",
    ):
        utils.create_public_tenant(domain, email)

    assert not TenantUser.objects.filter(email=email).exists()
    assert not Company.objects.filter(schema_name=get_public_schema_name()).exists()
    assert not Domain.objects.filter(domain=domain).exists()


@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_create_public_tenant_second_call_creates_nothing():
    """Ensures ExistsError is raised before creating a second owner/domain."""
    utils.create_public_tenant("domain1.test", "user1@domain.com")
    domain2 = "domain2.test"
    email2 = "user2@domain.com"

    with pytest.raises(ExistsError, match="Public tenant already exists"):
        utils.create_public_tenant(domain2, email2)

    assert not TenantUser.objects.filter(email=email2).exists()
    assert not Domain.objects.filter(domain=domain2).exists()


@patch("tenant_users.tenants.utils.get_tenant_model")
@pytest.mark.usefixtures("_tenant_type_settings")
@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_tenant_public_tenant_with_multitype(mock_get_tenant_model):
    """Tests that multi-type information is used during the Public Tenant creation."""
    mock_tenant_model = Mock()
    mock_tenant_model.objects.filter.return_value.first.return_value = None
    mock_get_tenant_model.return_value = mock_tenant_model

    # Since we're mocking, we expect an exception to be thrown after Tenant.create()
    with pytest.raises(ValueError, match='must be a "Company" instance'):
        utils.create_public_tenant("domain.test", "user@domain.com")

    # Check the mock was called
    assert mock_tenant_model.called

    # Get the arguments it was called with
    _, kwargs = mock_tenant_model.call_args

    # Ensure the multi-type database field was added during Tenant creation
    assert kwargs.get(settings.MULTI_TYPE_DATABASE_FIELD) == get_public_schema_name()  # type: ignore[misc]


@pytest.mark.django_db
@pytest.mark.no_db_setup
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


@pytest.mark.django_db
@pytest.mark.no_db_setup
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


@patch("tenant_users.tenants.utils.get_tenant_model")
@pytest.mark.django_db
@pytest.mark.no_db_setup
def test_tenant_public_tenant_save_verbosity(mock_get_tenant_model):
    """Tests that the verbosity parameter is correctly passed to save()."""
    mock_tenant_model = Mock()
    mock_tenant_model.objects.filter.return_value.first.return_value = None
    mock_get_tenant_model.return_value = mock_tenant_model

    # Since we're mocking, we expect an exception to be thrown after Tenant.create()
    with pytest.raises(ValueError, match='must be a "Company" instance'):
        utils.create_public_tenant("domain.test", "user@domain.com", verbosity=3)

    # Check the mock was called
    assert mock_tenant_model.called

    # Check that save() was called with the correct verbosity
    mock_tenant_instance = mock_tenant_model.return_value
    mock_tenant_instance.save.assert_called_once_with(verbosity=3)
