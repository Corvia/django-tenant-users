import uuid
from django.db import models
from tenant_users.tenants.models import UserProfile

_NameFieldLength = 64


class GuidUser(UserProfile):
    guid = models.UUIDField(default=uuid.uuid4, primary_key=True)


class TenantUser(UserProfile):
    """Simple user model definition for testing."""

    name = models.CharField(max_length=_NameFieldLength, blank=True)
