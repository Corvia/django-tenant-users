from django.contrib.auth import get_user_model

from tenant_users.permissions.models import UserTenantPermissions

TenantUser = get_user_model()


def test_permissions_mixin_facade(public_tenant, tenant_user):

    owner = public_tenant.owner

    assert (
        tenant_user != owner
    ), "The tenant_user should not be equal to the owner of the tenant because he cannot be removed."

    user_tenant_perms: UserTenantPermissions = tenant_user.tenant_perms
    user_tenant_perms.is_superuser = True
    user_tenant_perms.is_staff = True
    user_tenant_perms.save(update_fields=["is_superuser", "is_staff"])
    # Test permision of a member user

    assert tenant_user.is_superuser == True
    assert tenant_user.is_staff == True
    assert tenant_user.has_tenant_permissions() == True
    assert tenant_user.has_perm(perm="can_test") == True
    assert tenant_user.has_perms(perm_list=["can_test"]) == True
    assert tenant_user.has_module_perms(app_label="companies") == True

    public_tenant.remove_user(tenant_user)

    # Test permision of a non-member user
    assert tenant_user.has_tenant_permissions() == False
    assert tenant_user.is_staff == False
    assert tenant_user.is_superuser == False
    assert tenant_user.get_group_permissions() == set()
    assert tenant_user.get_all_permissions() == set()
    assert tenant_user.has_perm(perm="can_test") == False
    assert tenant_user.has_perms(perm_list=["can_test"]) == False
    assert tenant_user.has_module_perms(app_label="companies") == False
    # Test __str__ of UserTenantPermissions
    assert str(UserTenantPermissions.objects.get(profile=owner)) == str(owner)
