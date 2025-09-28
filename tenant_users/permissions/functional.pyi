from functools import cached_property
from typing import TypeVar, overload

_T = TypeVar("_T")

class tenant_cached_property(cached_property[_T]):
    @overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> tenant_cached_property[_T]: ...
    @overload
    def __get__(self, instance: object, owner: type | None = None) -> _T: ...
