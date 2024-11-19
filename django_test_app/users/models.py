import uuid
from django.db import models
from tenant_users.tenants.models import UserProfile
from django.conf import settings
from django.utils.translation import gettext_lazy as _
_NameFieldLength = 64


class TenantUser(UserProfile):
    """Simple user model definition for testing."""

    name = models.CharField(max_length=_NameFieldLength, blank=True)


class GuidUser(UserProfile):
    guid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    tenants = models.ManyToManyField(
        settings.TENANT_MODEL,
        verbose_name=_("tenants"),
        blank=True,
        help_text=_("The tenants this user belongs to."),
        related_name="guid_users_set",
    )
