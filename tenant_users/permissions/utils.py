from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from tenant_users.permissions.models import UserTenantPermissions


def get_optimized_tenant_perms_queryset() -> QuerySet[UserTenantPermissions]:
    """Return an optimized queryset for UserTenantPermissions.

    This is the recommended default optimizer that uses select_related to fetch
    the user profile in the same query, and prefetch_related to efficiently load
    groups. This avoids N+1 query problems when accessing permission-related data.

    Returns:
        QuerySet: An optimized UserTenantPermissions queryset with related data loaded.

    Example:
        In your settings.py:

        .. code-block:: python

            TENANT_USERS_PERMS_QUERYSET = (
                "tenant_users.permissions.utils.get_optimized_tenant_perms_queryset"
            )

    Note:
        This optimizer is suitable for most use cases where you need to access
        the user profile or groups along with permissions. If you have different
        requirements, you can create your own custom optimizer function.
    """
    from tenant_users.permissions.models import UserTenantPermissions  # noqa: PLC0415

    return UserTenantPermissions.objects.select_related("profile").prefetch_related(
        "groups"
    )
