import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from tenant_users.permissions.models import UserTenantPermissions

TenantUser = get_user_model()


@pytest.mark.django_db()
def test_get_group_permissions(tenant_user):
    # Create user

    # Create group
    group = Group.objects.create(name="testgroup")

    # Create permission
    permission = Permission.objects.create(
        codename="can_test",
        name="Can Test",
        content_type_id=1,  # Assuming content type ID is 1, adjust as necessary
    )
    perm_codename = f"{permission.content_type.app_label}.{permission.codename}"

    # Assign permission to group
    group.permissions.add(permission)

    # Assign group to user through UserTenantPermissions
    user_tenant_permissions = UserTenantPermissions.objects.get(profile=tenant_user)
    user_tenant_permissions.groups.add(group)
    assert tenant_user.has_perm(perm_codename)
