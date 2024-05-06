from django.core.management.base import BaseCommand

from tenant_users.tenants.models import ExistsError, SchemaError
from tenant_users.tenants.utils import create_public_tenant


class Command(BaseCommand):
    help = "Creates the initial public tenant"

    def add_arguments(self, parser):
        parser.add_argument("--domain_url", nargs=1, required=True, type=str,
                            help="The URL for the public tenant's domain.")
        parser.add_argument("--owner_email", nargs=1, required=True, type=str,
                            help="Email address of the owner user.")

    def handle(self, domain_url: str, owner_email: str, **kwargs):  # noqa: ARG002, kwargs must be here.
        try:
            create_public_tenant(domain_url=domain_url, owner_email=owner_email)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created public tenant with Domain URL ({domain_url}) and Owner ({owner_email})"
                )
            )
        except (ExistsError, SchemaError) as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error creating public tenant: {e}"
                )
            )
