from django.db import models


from tenant_users.compat import TENANT_SCHEMAS
from tenant_users.tenants.models import TenantBase


class Client(TenantBase):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

if not TENANT_SCHEMAS:
    from django_tenants.models import DomainMixin

    class Domain(DomainMixin):
        pass
