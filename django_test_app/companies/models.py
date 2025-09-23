from django.db import models
from django_tenants.models import DomainMixin

from tenant_users.tenants.models import TenantBase, schema_required

_NameFieldLength = 64


class Company(TenantBase):
    """Test Tenant object."""

    name = models.CharField(max_length=_NameFieldLength)
    description = models.TextField()
    type = models.CharField(max_length=100, default="type1")

    @schema_required
    def test_schema_method(self):
        """Simple test method to validate @schema_required behavior."""
        return f"Called on tenant: {self.schema_name}"


class Domain(DomainMixin):
    """This class is required for django_tenants."""
