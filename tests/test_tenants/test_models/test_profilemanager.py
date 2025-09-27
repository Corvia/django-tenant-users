import pytest
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, schema_context, tenant_context

from tenant_users.permissions.models import UserTenantPermissions
from tenant_users.tenants import models

#: Constants
TenantModel = get_tenant_model()
TenantUser = get_user_model()


@pytest.mark.django_db
def test_create_user_in_tenant_schema(test_tenants):
    """Ensures error is raised when user creation isn't in public schema."""
    tenant = test_tenants.first()
    with (
        schema_context(tenant.schema_name),
        pytest.raises(
            models.SchemaError,
            match="Schema must be public",
        ),
    ):
        TenantUser.objects.create_user(email="user@schema.com")


@pytest.mark.django_db
def test_create_user_no_email():
    """Ensures error is raised if email is missing."""
    with pytest.raises(ValueError, match="must have an email"):
        TenantUser.objects.create_user()


@pytest.mark.django_db
def test_create_user_with_password(client):
    """Ensures created user with password is valid."""
    secret = "Secret#"  # noqa: S105
    email = "user@test.com"
    user = TenantUser.objects.create_user(email, password=secret)

    assert user.has_usable_password() is True
    assert client.login(username=email, password=secret) is True


@pytest.mark.django_db
def test_create_user_without_password():
    """Ensures created user gets unusable password if excluded."""
    user = TenantUser.objects.create_user("user@test.com")
    assert user.has_usable_password() is False


@pytest.mark.django_db
def test_create_duplicate_user(tenant_user):
    """Ensures duplicate users can't exist."""
    with pytest.raises(models.ExistsError, match="User already exists"):
        TenantUser.objects.create_user(tenant_user.email)


@pytest.mark.django_db
def test_delete_user(tenant_user):
    """Ensure deleted user is inactive."""
    TenantUser.objects.delete_user(tenant_user)
    tenant_user.refresh_from_db()

    assert tenant_user.is_active is False


@pytest.mark.django_db
def test_delete_public_owner(public_tenant):
    """Ensure inability to delete public tenant owner."""
    with pytest.raises(
        models.DeleteError,
        match="Cannot delete the public tenant owner",
    ):
        TenantUser.objects.delete_user(public_tenant.owner)


@pytest.mark.django_db
def test_delete_tenant_owner(create_tenant, public_tenant):
    """Ensure tenant is disabled when owner is deleted."""
    # Create a temp tenant with new user
    user = TenantUser.objects.create_user("temp@tenant.com")
    tenant = create_tenant(user, "pytesttemp")

    # Action below
    TenantUser.objects.delete_user(user)
    tenant.refresh_from_db()

    assert tenant.owner == public_tenant.owner


@pytest.mark.django_db
def test_delete_user_removes_permissions_from_all_tenants(test_tenants):
    """Ensure delete_user removes UserTenantPermissions from all tenant schemas.

    This test verifies that when a user exists in multiple tenants and has different
    UserTenantPermissions primary keys in each schema (due to auto-increment sequences
    being schema-specific), the delete_user method properly removes ALL permissions
    across all schemas. The dummy user is added first to tenant_a to ensure the
    target user gets different UTP primary keys in each schema, which can expose
    issues with Django's OneToOneField caching behavior across schema boundaries.
    """
    tenant_a, tenant_b = test_tenants[0], test_tenants[1]

    target_user = TenantUser.objects.create_user("target@test.com")
    dummy_user = TenantUser.objects.create_user("dummy@test.com")

    # Add dummy user to tenant_a first to ensure different UserTenantPermissions PKs
    tenant_a.add_user(dummy_user)
    tenant_a.add_user(target_user)
    tenant_b.add_user(target_user)

    # Verify target_user has permissions in both tenants
    with tenant_context(tenant_a):
        assert UserTenantPermissions.objects.filter(profile_id=target_user.pk).exists()

    with tenant_context(tenant_b):
        assert UserTenantPermissions.objects.filter(profile_id=target_user.pk).exists()

    # Delete the user - should remove ALL UserTenantPermissions across all schemas
    TenantUser.objects.delete_user(target_user)

    # Verify no UserTenantPermissions remain in any tenant schema
    with tenant_context(tenant_a):
        assert not UserTenantPermissions.objects.filter(
            profile_id=target_user.pk
        ).exists()

    with tenant_context(tenant_b):
        assert not UserTenantPermissions.objects.filter(
            profile_id=target_user.pk
        ).exists()
