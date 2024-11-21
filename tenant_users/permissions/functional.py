from django.db import connection
from django.utils.functional import cached_property


class tenant_cached_property(cached_property):  # noqa: N801
    """A tenant-aware implementation of Django's cached_property decorator.

    This class extends Django's `cached_property` decorator, adding tenant-awareness to
    the property caching mechanism. It is particularly useful for properties that
    should be cached on a per-tenant basis.

    Methods:
        __get__: Retrieves the value of the cached property, specific to the current tenant.
                 If the instance is None, returns the property descriptor itself. Otherwise,
                 it returns the property value, caching it under the current tenant's schema
                 if not already cached.
    """

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        if "_tenant_cache" not in instance.__dict__:
            instance.__dict__["_tenant_cache"] = {}

        tenant_cache = instance.__dict__["_tenant_cache"]
        current_schema = connection.schema_name

        if current_schema not in tenant_cache:
            tenant_cache[current_schema] = {}
            tenant_cache[current_schema][self.name] = self.func(instance)
        elif self.name not in tenant_cache[current_schema]:
            tenant_cache[current_schema][self.name] = self.func(instance)

        return tenant_cache[current_schema][self.name]

