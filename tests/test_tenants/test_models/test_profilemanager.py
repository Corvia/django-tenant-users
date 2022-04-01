import pytest
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, schema_context

from tenant_users.tenants import models

#: Constants
TenantModel = get_tenant_model()
TenantUser = get_user_model()


@pytest.mark.django_db()
def test_create_user_in_tenant_schema(test_tenants):
    """Ensures error is raised when user creation isn't in public schema."""
    tenant = test_tenants.first()
    with schema_context(tenant.schema_name):
        with pytest.raises(models.SchemaError, match='Schema must be public'):
            TenantUser.objects.create_user(email='user@schema.com')


@pytest.mark.django_db()
def test_create_user_no_email():
    """Ensures error is raised if email is missing."""
    with pytest.raises(ValueError, match='must have an email'):
        TenantUser.objects.create_user()


@pytest.mark.django_db()
def test_create_user_with_password(client):
    """Ensures created user with password is valid."""
    secret = 'Secret#'
    email = 'user@test.com'
    user = TenantUser.objects.create_user(email, password=secret)

    assert user.has_usable_password() is True
    assert client.login(username=email, password=secret) is True


@pytest.mark.django_db()
def test_create_user_without_password():
    """Ensures created user gets unusable password if excluded."""
    user = TenantUser.objects.create_user('user@test.com')
    assert user.has_usable_password() is False


@pytest.mark.django_db()
def test_create_duplicate_user(tenant_user):
    """Ensures duplicate users can't exist."""
    with pytest.raises(models.ExistsError, match='User already exists'):
        TenantUser.objects.create_user(tenant_user.email)


@pytest.mark.django_db()
def test_delete_user(tenant_user):
    """Ensure deleted user is inactive."""
    TenantUser.objects.delete_user(tenant_user)
    tenant_user.refresh_from_db()

    assert tenant_user.is_active is False


@pytest.mark.django_db()
def test_delete_public_owner(public_tenant):
    """Ensure inability to delete public tenant owner."""
    with pytest.raises(
        models.DeleteError,
        match='Cannot delete the public tenant owner',
    ):
        TenantUser.objects.delete_user(public_tenant.owner)


@pytest.mark.django_db()
def test_delete_tenant_owner(create_tenant, public_tenant):
    """Ensure tenant is disabled when owner is deleted."""
    # Create a temp tenant with new user
    user = TenantUser.objects.create_user('temp@tenant.com')
    tenant = create_tenant(user, 'pytesttemp')

    # Action below
    TenantUser.objects.delete_user(user)
    tenant.refresh_from_db()

    assert tenant.owner == public_tenant.owner
