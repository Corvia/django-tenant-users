from django.urls import reverse
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from users.models import TenantUser

from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant


class MainView(TemplateView):
    template_name = 'core/main.html'


class CreateUser(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        create_public_tenant("www.my_domain.com", "admin@my_domain.com")

        TenantUser.objects.create_user(email="user@my_domain.com", password='password', is_active=True)

        return reverse('main')


class CreateSuperUser(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):

        TenantUser.objects.create_superuser(email="superuser@my_domain.com", password='password', is_active=True)

        return reverse('main')


class CreateTenant(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        fqdn = provision_tenant("Domain1", "domain1", "user@my_domain.com")

        return reverse('main')