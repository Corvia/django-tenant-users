from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, ClassVar

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from tenant_users.tenants.models import UserProfile, UserProfileManager

_NameFieldLength = 64

if TYPE_CHECKING:
    from django_test_app.companies.models import Company


class TenantUser(UserProfile):
    """Simple user model definition for testing."""

    name = models.CharField(max_length=_NameFieldLength, blank=True)

    # ---- Typing Examples for django-tenant-users users ----
    # If you want typing in your app, add annotations like these to your models.

    # Type the custom manager with the specific model type
    objects: ClassVar[UserProfileManager[TenantUser]]

    # Type the reverse accessor created by Company.owner
    company_set: models.Manager[Company]

    # Be more specific since we type as [Any, Any] in UserProfile base class
    tenants: models.ManyToManyField[Company, Company]


class GuidUser(UserProfile):
    guid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=_NameFieldLength, blank=True)
    tenants = models.ManyToManyField(
        settings.TENANT_MODEL,
        verbose_name=_("tenants"),
        blank=True,
        help_text=_("The tenants this user belongs to."),
        related_name="guid_users_set",
    )
