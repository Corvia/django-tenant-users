import pytest
from django.contrib.auth import get_user_model
from hypothesis import given, settings
from hypothesis.extra import django

from tenant_users.tenants.models import DeleteError

#: Constants
TenantUser = get_user_model()


@pytest.mark.django_db()
@given(django.from_model(TenantUser))
@settings(deadline=None)
def test_model_properties(instance: TenantUser) -> None:
    """Tests that instance can be saved and has correct representation."""
    # Test UserProfile.has_verified_email()
    assert instance.has_verified_email() == instance.is_verified

    # Test UserProfile.get_full_name()
    assert instance.get_full_name() == str(instance)

    # Test UserProfile.get_short_name()
    assert instance.get_short_name() == instance.email


@pytest.mark.django_db()
@given(django.from_model(TenantUser))
@settings(deadline=None, max_examples=1)
def test_user_delete(instance: TenantUser) -> None:
    """Tests tenants.models.UserProfile.delete scenarios."""
    # Test UserProfile.delete()
    with pytest.raises(
        DeleteError,
        match=r"delete_user\(\) should be used",
    ):
        instance.delete()

    # Force drop UserProfile
    instance.delete(force_drop=True)
    assert TenantUser.objects.filter(email=instance.email).exists() is False
