# Support both django-tenant-schemas and django-tenants packages
try:
    from django_tenants.test.cases import TenantTestCase
    from django_tenants.utils import get_public_schema_name, get_tenant_model
    from django_tenants.models import TenantMixin

except ImportError as e:
    from tenant_schemas.test.cases import TenantTestCase
    from tenant_schemas.utils import get_public_schema_name, get_tenant_model
    from tenant_schemas.models import TenantMixin
