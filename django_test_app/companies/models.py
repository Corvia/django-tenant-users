from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django_tenants.models import DomainMixin

from tenant_users.tenants.models import TenantBase, schema_required

_NameFieldLength = 64

if TYPE_CHECKING:
    from django.db.models.expressions import Combinable

    from django_test_app.users.models import TenantUser


class Company(TenantBase):
    """Test Tenant object."""

    name = models.CharField(max_length=_NameFieldLength)
    description = models.TextField()
    type = models.CharField(max_length=100, default="type1")

    # ---- Typing Examples for django-tenant-users users ----
    # If you want typing in your app, add annotations like these to your models.

    # Type the default manager to return the correct model type
    objects: models.Manager[Company] = models.Manager()

    # Type the ForeignKey with union for expressions and the related model
    owner: models.ForeignKey[TenantUser | Combinable, TenantUser]

    @schema_required
    def test_schema_method(self):
        """Simple test method to validate @schema_required behavior."""
        return f"Called on tenant: {self.schema_name}"


class Domain(DomainMixin):
    """This class is required for django_tenants."""
