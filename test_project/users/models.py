from django.db import models

from tenant_users.tenants.models import UserProfile
from test_project.settings import CHAR_LENGTH


class TenantUser(UserProfile):
    """Simple user model definition for testing."""

    name = models.CharField(max_length=CHAR_LENGTH, blank=True)
