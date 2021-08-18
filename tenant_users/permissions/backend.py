from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

from tenant_users.permissions.models import UserTenantPermissions


class UserBackend(ModelBackend):
    """
    Authenticates against UserProfile
    Authorizes against the UserTenantPermissions.
    The Facade classes handle the magic of passing
    requests to the right spot.
    """

    # We override this so that it looks for the 'groups' attribute on the
    # UserTenantPermissions rather than from get_user_model()
    def _get_group_permissions(self, user_obj):
        user_groups_field = UserTenantPermissions._meta.get_field('groups')
        user_groups_query = 'group__{0}'.format(
            user_groups_field.related_query_name(),
        )
        return Permission.objects.filter(**{user_groups_query: user_obj})
