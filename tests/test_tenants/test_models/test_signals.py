from unittest.mock import patch

import pytest

from django_test_app.users.models import TenantUser


@pytest.mark.django_db
@patch("tenant_users.tenants.models.tenant_user_created.send")
def test_user_created_signal(mock):
    """Ensure signal is sent for delete_user()."""
    TenantUser.objects.create_user("created@signal.com", "secret123")
    assert mock.called is True
    assert mock.call_count == 1


@pytest.mark.django_db
@patch("tenant_users.tenants.models.tenant_user_deleted.send")
def test_user_deleted_signal(mock, tenant_user):
    """Ensure signal is sent for delete_user()."""
    TenantUser.objects.delete_user(tenant_user)
    assert mock.called is True
    assert mock.call_count == 1
