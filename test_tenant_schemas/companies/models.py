from django.db import models

from tenant_users.tenants.models import TenantBase

_NameFieldLength = 64


class Company(TenantBase):
    """Test Tenant object."""

    name = models.CharField(max_length=_NameFieldLength, blank=True)
    description = models.TextField()
