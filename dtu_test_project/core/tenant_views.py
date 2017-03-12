from django.urls import reverse
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from users.models import TenantUser

from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant


class TenantView(TemplateView):
    template_name = 'core/tenant.html'

