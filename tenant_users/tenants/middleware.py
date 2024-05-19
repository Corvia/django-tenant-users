from typing import Callable

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _


class TenantAccessMiddleware:
    """Middleware to ensure the user has access to the requested tenant.

    If the user is authenticated but does not have access to the requested
    tenant, a 404 error is raised. Unauthenticated users are allowed to proceed.

    Attributes:
        get_response (Callable): The next middleware or view to be called.
        error_message (str): Customizable error message for unauthorized access.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Initialize the middleware.

        Args:
            get_response (Callable): The next middleware or view to be called.
        """
        self.get_response = get_response
        self.error_message = getattr(
            settings,
            "TENANT_USERS_ACCESS_ERROR_MESSAGE",
            _("Access to this resource is denied."),
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and check tenant access.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            HttpResponse: The response object from the next middleware or view.

        Raises:
            Http404: If the user does not have access to the requested tenant.
        """
        if not self.has_tenant_access(request):
            raise Http404(self.error_message)

        return self.get_response(request)

    def has_tenant_access(self, request: HttpRequest) -> bool:
        """Check if the user has access to the requested tenant.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            bool: True if the user has access or is unauthenticated, False otherwise.
        """
        if not request.user.is_authenticated:
            return True

        return request.user.tenants.filter(id=request.tenant.id).exists()
