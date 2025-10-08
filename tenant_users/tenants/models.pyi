from datetime import datetime
from typing import Any, Callable, ClassVar, TypeVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.dispatch import Signal
from django_tenants.models import TenantMixin

from tenant_users.permissions.models import PermissionsMixinFacade

# TypeVars
_UserProfileT = TypeVar("_UserProfileT", bound=AbstractBaseUser)

# Signals
tenant_user_removed: Signal
tenant_user_added: Signal
tenant_user_created: Signal
tenant_user_deleted: Signal

class InactiveError(Exception): ...
class ExistsError(Exception): ...
class DeleteError(Exception): ...
class SchemaError(Exception): ...

def schema_required(func: Callable[..., Any]) -> Callable[..., Any]: ...

class TenantBase(TenantMixin):
    slug: models.SlugField[str, str]
    owner: models.ForeignKey[Any, Any]
    created: models.DateTimeField[datetime, datetime]
    modified: models.DateTimeField[datetime, datetime]
    auto_create_schema: bool
    auto_drop_schema: bool
    user_set: models.Manager[Any]

    def delete(self, *args: Any, force_drop: bool = False, **kwargs: Any) -> None: ...
    def add_user(
        self,
        user_obj: Any,
        *,
        is_superuser: bool = False,
        is_staff: bool = False,
    ) -> None: ...
    def remove_user(self, user_obj: Any) -> None: ...
    def delete_tenant(self) -> None: ...
    def transfer_ownership(self, new_owner: Any) -> None: ...

class UserProfileManager(BaseUserManager[_UserProfileT]):
    def _create_user(
        self,
        email: str,
        password: str | None,
        *,
        is_staff: bool = False,
        is_superuser: bool = False,
        is_verified: bool = False,
        **extra_fields: Any,
    ) -> _UserProfileT: ...
    def create_user(
        self,
        email: str | None = None,
        password: str | None = None,
        *,
        is_staff: bool = False,
        **extra_fields: Any,
    ) -> _UserProfileT: ...
    def create_superuser(
        self,
        password: str,
        email: str,
        **extra_fields: Any,
    ) -> _UserProfileT: ...
    def delete_user(self, user_obj: _UserProfileT) -> None: ...

class UserProfile(AbstractBaseUser, PermissionsMixinFacade):
    USERNAME_FIELD: str
    objects: ClassVar[UserProfileManager[Any]]
    tenants: models.ManyToManyField[Any, Any]
    email: models.EmailField[str, str]
    is_verified: models.BooleanField[bool, bool]

    class Meta:
        abstract: bool

    def has_verified_email(self) -> bool: ...
    def delete(
        self,
        *args: Any,
        force_drop: bool = False,
        **kwargs: Any,
    ) -> tuple[int, dict[str, int]]: ...
    def get_short_name(self) -> str: ...
    def get_full_name(self) -> str: ...
