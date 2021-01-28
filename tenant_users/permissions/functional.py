from django.db import connection

class tenant_cached_property:
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    A cached property can be made out of an existing method:
    (e.g. ``url = cached_property(get_absolute_url)``).
    The optional ``name`` argument is obsolete as of Python 3.6 and will be
    deprecated in Django 4.0 (#30127).
    """

    name = None

    @staticmethod
    def func(instance):
        raise TypeError(
            'Cannot use cached_property instance without calling '
            '__set_name__() on it.'
        )

    def __init__(self, func, name=None):
        self.real_func = func
        self.__doc__ = getattr(func, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                "(%r and %r)." % (self.name, name)
            )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        current_schema = connection.schema_name

        if current_schema not in instance.__dict__.keys():
            instance.__dict__[current_schema] = {}
            res = instance.__dict__[current_schema][self.name] = self.func(
                instance
            )
            return res

        elif self.name not in instance.__dict__[current_schema].keys():
            res = instance.__dict__[current_schema][self.name] = self.func(
                instance
            )
            return res

        res = instance.__dict__[current_schema][self.name]
        return res
