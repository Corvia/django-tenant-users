from django.db import connection
from django.utils.functional import cached_property


class tenant_cached_property(cached_property):
    """
    Tenant-aware version of the ``cached_property`` decorator
    from ``django.utils.functional``.
    """

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        current_schema = connection.schema_name

        if current_schema not in instance.__dict__:
            instance.__dict__[current_schema] = {}
            res = instance.__dict__[current_schema][self.name] = self.func(instance)
            return res

        elif self.name not in instance.__dict__[current_schema]:
            res = instance.__dict__[current_schema][self.name] = self.func(instance)
            return res

        res = instance.__dict__[current_schema][self.name]
        return res
