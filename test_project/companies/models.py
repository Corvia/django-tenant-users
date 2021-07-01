from django.db import models

from tenant_users.compat import TENANT_SCHEMAS
from tenant_users.tenants.models import TenantBase
from test_project.settings import CHAR_LENGTH


class Company(TenantBase):
    """Test Tenant object."""

    name = models.CharField(max_length=CHAR_LENGTH, blank=True)
    description = models.TextField()


if not TENANT_SCHEMAS:
    from django_tenants.models import DomainMixin  # noqa: WPS433

    class Domain(DomainMixin):
        """This class is required for django_tenants."""
