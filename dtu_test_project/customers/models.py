from django.db import models
from tenant_users.companies.models import Company


class Client(Company):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
