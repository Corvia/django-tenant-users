import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django_tenants.utils import (
    get_public_schema_name,
    get_tenant_model,
    tenant_context,
)

from tenant_users.permissions.models import UserTenantPermissions
from tenant_users.tenants.models import (
    TENANT_DELETE_ERROR_MESSAGE,
    DeleteError,
    ExistsError,
)
from tenant_users.tenants.tasks import provision_tenant

#: Constants
TenantModel = get_tenant_model()
UserModel = get_user_model()


def test_provision_with_schema_name(tenant_user) -> None:
    """Test tenant provisioning with a custom schema name.

    This test verifies that the `provision_tenant` function correctly creates a tenant
    with a custom schema name and that the corresponding schema is created in the database.
    """
    slug = "sample"
    custom_schema_name = "my_custom_name"
    tenant, _ = provision_tenant(
        tenant_name="Sample Tenant",
        tenant_slug=slug,
        owner=tenant_user,
        schema_name=custom_schema_name,
    )
    owner = tenant.owner

    with pytest.raises(
        ExistsError, match="User already added to tenant: tenant-user@test.com"
    ):
        tenant.add_user(owner)
    error_message = f"Cannot remove owner from tenant: {owner}"
    with pytest.raises(DeleteError, match=error_message):
        tenant.remove_user(owner)


def test_deleting_a_provision_tenant(tenant_user) -> None:
    """Test tenant provisioning with a custom schema name.

    This test verifies that the `provision_tenant` function correctly creates a tenant
    with a custom schema name and that the corresponding schema is created in the database.
    """
    slug = "sample"
    custom_schema_name = "my_custom_name"
    tenant, _ = provision_tenant(
        "Sample Tenant",
        slug,
        tenant_user,
        schema_name=custom_schema_name,
    )
    # Test using delete (NOT ALLOWED)
    with pytest.raises(DeleteError, match=TENANT_DELETE_ERROR_MESSAGE):
        tenant.delete()
    # create another user to test deleteting a tenant with multiple users

    another_user = UserModel.objects.create_user(
        email="testing2@test.com", name="testing user"
    )
    tenant.add_user(another_user)

    tenant.delete_tenant()
    public_tenant = get_tenant_model().objects.get(
        schema_name=get_public_schema_name(),
    )

    assert public_tenant.owner == tenant.owner
    assert tenant.user_set.count() == 1
    with tenant_context(tenant):

        # Verify that the public owner retains permission to the provisioned tenant after deletion
        public_owner_has_permission = UserTenantPermissions.objects.filter(
            profile=tenant.owner
        ).exists()
        assert (
            public_owner_has_permission
        ), "The public owner should retain permission to the provisioned tenant after deletion."

        # Verify that the previous owner does not retain permission to the provisioned tenant after deletion
        previous_owner_has_permission = UserTenantPermissions.objects.filter(
            profile=another_user
        ).exists()
        assert (
            previous_owner_has_permission == False
        ), "The previous owner should not retain permission to the provisioned tenant after deletion."


def test_delete_provisioned_tenant_with_assigned_user_roles(tenant_user):
    # Create user
    slug = "sample"
    custom_schema_name = "my_custom_name"
    tenant, _ = provision_tenant(
        "Sample Tenant",
        slug,
        tenant_user,
        schema_name=custom_schema_name,
    )
    owner = tenant.owner
    assert owner == tenant_user
    with tenant_context(tenant):
        # Create group
        group = Group.objects.create(name="testgroup")

        # Create a test permission
        permission = Permission.objects.create(
            codename="can_test",
            name="Can Test",
            content_type_id=1,
        )

        # Assign permission to group
        group.permissions.add(permission)

        # Assign group or role to user through UserTenantPermissions
        owner.tenant_perms.groups.add(group)
        tenant.delete_tenant()
        public_tenant = get_tenant_model().objects.get(
            schema_name=get_public_schema_name(),
        )
        ##Ensure user is removed inspite of having any role in the tenant
        assert UserTenantPermissions.objects.filter(profile=owner).exists() == False
    assert public_tenant.owner == tenant.owner
    assert UserTenantPermissions.objects.filter(profile=public_tenant.owner).exists()


def test_transfer_ownership_to_existing_user(test_tenants, public_tenant):

    tenant = test_tenants.first()
    assert tenant.owner != public_tenant.owner, "Can't transfer ownership to same owner"
    with tenant_context(tenant):

        tenant.add_user(public_tenant.owner)
        # Assign group or role to user through UserTenantPermissions
        tenant.transfer_ownership(public_tenant.owner)

        ##Ensure user is removed inspite of having any role in the tenant
        assert UserTenantPermissions.objects.filter(
            profile=public_tenant.owner
        ).exists()
        assert (
            UserTenantPermissions.objects.get(profile=public_tenant.owner).is_superuser
            == True
        )
