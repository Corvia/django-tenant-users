from http import HTTPStatus

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import Http404, HttpResponse
from django.test import RequestFactory

from tenant_users.tenants.middleware import TenantAccessMiddleware


class NoOpCallable:
    """A no-operation callable class."""

    def __call__(self, request):  # noqa: ARG002
        return HttpResponse(status=HTTPStatus.ACCEPTED)


@pytest.mark.django_db()
class TestTenantAccessMiddleware:
    """Tests for the TenantAccessMiddleware class."""

    @pytest.fixture(autouse=True)
    def _setup(self, create_tenant, tenant_user_admin, tenant_user):
        """Fixture to set up a tenant and a tenant user for tests.

        Args:
            create_tenant (function): Factory function to create a tenant.
            tenant_user_admin (User): Admin user for the tenant.
            tenant_user (User): Regular user to be used in tests.
        """
        self.tenant = create_tenant(tenant_user_admin, "middleware")
        self.tenant_user = tenant_user

        # Setup test request
        self.request = RequestFactory().get("/fake-url/")
        self.request.tenant = self.tenant
        self.request.user = tenant_user

        # Setup Middeware
        self.middleware = TenantAccessMiddleware(NoOpCallable())

        # Cleanup after each test to reset user tenants
        yield
        if self.tenant in tenant_user.tenants.all():
            self.tenant.remove_user(tenant_user)

    def test_authenticated_user_has_access(self, tenant_user):
        """Test middleware allows access for user with tenant access.

        Args:
            tenant_user (User): The tenant user to be tested.
        """
        self.tenant.add_user(tenant_user)

        # Check to ensure user is member of tenant
        assert self.tenant in tenant_user.tenants.all()

        response = self.middleware(self.request)

        assert response.status_code == HTTPStatus.ACCEPTED

    def test_authenticated_user_no_access(self, tenant_user):
        """Test middleware denies access for user without tenant access.

        Args:
            tenant_user (User): The tenant user to be tested.
        """
        middleware = TenantAccessMiddleware(NoOpCallable())

        with pytest.raises(Http404) as err_info:
            middleware(self.request)

        assert str(err_info.value) == "Access to this resource is denied."
        assert self.tenant not in tenant_user.tenants.all()

    def test_unauthenticated(self):
        """Test middleware denies access for unauthenticated user."""
        self.request.user = AnonymousUser()

        response = self.middleware(self.request)

        # Middleware should proceed downstream
        assert response.status_code == HTTPStatus.ACCEPTED

    def test_custom_error_message(self, settings, tenant_user):
        """Test middleware raises custom error message from settings.

        Args:
            settings (Settings): Pytest fixture to temporarily set Django settings.
            tenant_user (User): The tenant user to be tested.
        """
        custom_message = "Custom access denied message."
        settings.TENANT_ACCESS_ERROR_MESSAGE = custom_message

        middleware = TenantAccessMiddleware(NoOpCallable())

        with pytest.raises(Http404) as err_info:
            middleware(self.request)

        assert str(err_info.value) == custom_message
        assert self.tenant not in tenant_user.tenants.all()
