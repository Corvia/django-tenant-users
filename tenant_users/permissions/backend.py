from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

from tenant_users.permissions.models import UserTenantPermissions


class UserBackend(ModelBackend):
    """Custom authentication backend for UserProfile.

    This backend authenticates users against the UserProfile and authorizes them
    based on UserTenantPermissions. It utilizes Facade classes to direct requests
    appropriately.

    Overrides:
        _get_group_permissions: Modified to refer to 'groups' attribute in
        UserTenantPermissions instead of the default user model's groups.

    Methods:
        _get_group_permissions: Retrieves group permissions associated with a given user.
    """

    def _get_group_permissions(self, user_obj):
        user_groups_field = UserTenantPermissions._meta.get_field(  # noqa: SLF001
            "groups"
        )
        user_groups_query = f"group__{user_groups_field.related_query_name()}"
        return Permission.objects.filter(**{user_groups_query: user_obj})
