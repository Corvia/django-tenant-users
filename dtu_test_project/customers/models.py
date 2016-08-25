from django.db import models
from tenant_users.tenants.models import TenantBase


class Client(TenantBase):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
