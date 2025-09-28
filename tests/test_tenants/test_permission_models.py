from django_test_app.companies.models import Company
from django_test_app.users.models import TenantUser
from tenant_users.permissions.models import UserTenantPermissions


def test_tenant_user_not_equal_to_owner(
    public_tenant: Company, tenant_user: TenantUser
) -> None:
    """Test that tenant_user is not equal to the owner."""
    owner = public_tenant.owner
    assert tenant_user != owner, (
        "The tenant_user should not be equal to the owner of the tenant because he cannot be removed."
    )


def test_user_tenant_permissions_basic_properties(tenant_user: TenantUser) -> None:
    """Test basic authentication properties of UserTenantPermissions."""
    user_tenant_perms = tenant_user.tenant_perms
    assert user_tenant_perms.is_active is True
    assert user_tenant_perms.is_anonymous is False
    assert user_tenant_perms.is_authenticated is True


def test_member_user_permissions(tenant_user: TenantUser) -> None:
    """Test permissions for a user who is a member of the tenant."""
    user_tenant_perms = tenant_user.tenant_perms
    user_tenant_perms.is_superuser = True
    user_tenant_perms.is_staff = True
    user_tenant_perms.save(update_fields=["is_superuser", "is_staff"])

    # Verify member permissions
    assert tenant_user.is_superuser
    assert tenant_user.is_staff
    assert tenant_user.has_tenant_permissions()
    assert tenant_user.has_perm(perm="can_test")
    assert tenant_user.has_perms(perm_list=["can_test"])
    assert tenant_user.has_module_perms(app_label="companies")


def test_non_member_user_permissions(
    public_tenant: Company, tenant_user: TenantUser
) -> None:
    """Test permissions for a user who is NOT a member of the tenant."""
    # Remove user from tenant to test non-member behavior
    public_tenant.remove_user(tenant_user)

    # Verify non-member permissions (should all be False/empty)
    assert not tenant_user.has_tenant_permissions()
    assert not tenant_user.is_staff
    assert not tenant_user.is_superuser
    assert tenant_user.get_group_permissions() == set()
    assert tenant_user.get_all_permissions() == set()
    assert not tenant_user.has_perm(perm="can_test")
    assert not tenant_user.has_perms(perm_list=["can_test"])
    assert not tenant_user.has_module_perms(app_label="companies")


def test_user_tenant_permissions_string_representation(public_tenant: Company) -> None:
    """Test __str__ method of UserTenantPermissions."""
    owner = public_tenant.owner
    user_tenant_permissions = UserTenantPermissions.objects.get(profile=owner)
    assert str(user_tenant_permissions) == str(owner)
