from django.contrib.auth.backends import ModelBackend
from guardian.backends import ObjectPermissionBackend, ObjectPermissionChecker, check_support
from django.contrib.auth.models import Permission
from .models import UserTenantPermissions
from guardian.utils import get_content_type, get_group_obj_perms_model, get_user_obj_perms_model
from guardian.exceptions import WrongAppError
from tenant_users.tenants.utils import get_tenant_identity


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
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})


class UserObjectBackend(ObjectPermissionBackend):
    def has_perm(self, user_obj, perm, obj=None):
        """
        The goal here is to replace the ObjectPermissionChecker call to a modified tenant aware version

        Returns ``True`` if given ``user_obj`` has ``perm`` for ``obj``. If no
        ``obj`` is given, ``False`` is returned.

        .. note::

           Remember, that if user is not *active*, all checks would return
           ``False``.

        Main difference between Django's ``ModelBackend`` is that we can pass
        ``obj`` instance here and ``perm`` doesn't have to contain
        ``app_label`` as it can be retrieved from given ``obj``.

        **Inactive user support**

        If user is authenticated but inactive at the same time, all checks
        always returns ``False``.
        """

        # check if user_obj and object are supported
        support, user_obj = check_support(user_obj, obj)
        if not support:
            return False

        if '.' in perm:
            app_label, perm = perm.split('.')
            if app_label != obj._meta.app_label:
                # Check the content_type app_label when permission
                # and obj app labels don't match.
                ctype = get_content_type(obj)
                if app_label != ctype.app_label:
                    raise WrongAppError("Passed perm has app label of '%s' while "
                                        "given obj has app label '%s' and given obj"
                                        "content_type has app label '%s'" %
                                        (app_label, obj._meta.app_label, ctype.app_label))

        check = TenantObjectPermissionChecker(user_obj)
        return check.has_perm(perm, obj)


class TenantObjectPermissionChecker(ObjectPermissionChecker):
    def __init__(self, user_or_group=None):
        # The constructor is replaced in order to call the get_tenant_identity method that is "tenant aware"
        self.user, self.group = get_tenant_identity(user_or_group)
        self._obj_perms_cache = {}

    def get_group_filters(self, obj):
        # We override this so that it looks for the 'groups' attribute on the
        # UserTenantPermissions rather than from user model
        ctype = get_content_type(obj)

        group_model = get_group_obj_perms_model(obj)
        group_rel_name = group_model.permission.field.related_query_name()
        if self.user:
            fieldname = '%s__group__%s' % (
                group_rel_name,
                UserTenantPermissions._meta.get_field('groups').related_query_name(),
            )
            group_filters = {fieldname: self.user}
        else:
            group_filters = {'%s__group' % group_rel_name: self.group}
        if group_model.objects.is_generic():
            group_filters.update({
                '%s__content_type' % group_rel_name: ctype,
                '%s__object_pk' % group_rel_name: obj.pk,
            })
        else:
            group_filters['%s__content_object' % group_rel_name] = obj

        return group_filters

    def get_user_filters(self, obj):
        ctype = get_content_type(obj)
        model = get_user_obj_perms_model(obj)
        related_name = model.permission.field.related_query_name()
        # Here we override this method to look for the associated profile instead of the user
        user_filters = {'%s__user' % related_name: self.user.profile}
        if model.objects.is_generic():
            user_filters.update({
                '%s__content_type' % related_name: ctype,
                '%s__object_pk' % related_name: obj.pk,
            })
        else:
            user_filters['%s__content_object' % related_name] = obj

        return user_filters
