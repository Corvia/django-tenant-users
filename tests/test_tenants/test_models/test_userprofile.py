import pytest
from django.contrib.auth import get_user_model
from hypothesis import given, settings
from hypothesis.extra import django

from tenant_users.tenants.models import DeleteError

#: Constants
TenantUser = get_user_model()


class TestUserProfile(django.TestCase):
    """This is a property-based test that ensures model correctness."""

    @given(django.from_model(TenantUser))
    @settings(deadline=None)
    def test_model_properties(self, instance: TenantUser) -> None:
        """Tests that instance can be saved and has correct representation."""
        instance.save()

        # Test UserProfile.has_verified_email()
        assert instance.has_verified_email() == instance.is_verified

        # Test UserProfile.get_full_name()
        assert instance.get_full_name() == str(instance)

        # Test UserProfile.get_short_name()
        assert instance.get_short_name() == instance.email

    @given(django.from_model(TenantUser))
    def test_user_delete(self, instance: TenantUser) -> None:
        """Tests tenants.models.UserProfile.delete scenarios."""
        # Test UserProfile.delete()
        with pytest.raises(
            DeleteError,
            match=r'delete_user\(\) should be used',
        ):
            instance.delete()

        # Force drop UserProfile
        instance.delete(force_drop=True)
        assert TenantUser.objects.filter(email=instance.email).exists() is False
