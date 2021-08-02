from django.db import models
from django_tenants.models import DomainMixin

from tenant_users.tenants.models import TenantBase

_NameFieldLength = 64


class Company(TenantBase):
    """Test Tenant object."""

    name = models.CharField(max_length=_NameFieldLength)
    description = models.TextField()


class Domain(DomainMixin):
    """This class is required for django_tenants."""
