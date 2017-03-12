from django.core.management.base import BaseCommand
from users.models import TenantUser

from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant


class Command(BaseCommand):
    help = 'Setups DTU'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        create_public_tenant("example.com", "admin@example.com")
        TenantUser.objects.create_superuser(email="superuser@example.com", password='password', is_active=True)

        TenantUser.objects.create_user(email="tenant1@example.com", password='password', is_active=True, is_staff=True)
        provision_tenant("Tenant1", "tenant1", "tenant1@example.com")

        TenantUser.objects.create_user(email="tenant2@example.com", password='password', is_active=True, is_staff=True)
        provision_tenant("Tenant2", "tenant2", "tenant2@example.com")
        print('Done')



