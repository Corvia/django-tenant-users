import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from tenant_users import compat
from tenant_users.tenants import tasks
from tenant_users.tenants.models import ExistsError, InactiveError

#: Constants
TenantModel = compat.get_tenant_model()
TenantUser = get_user_model()


@pytest.mark.django_db()
def test_provision_tenant(tenant_user_admin):
    """Tests tasks.provision_tenant() for correctness."""
    slug = 'sample'
    tenant_domain = tasks.provision_tenant(
        'Sample Tenant',
        slug,
        tenant_user_admin,
    )
    
    assert tenant_domain == _get_tenant_domain(slug)
    

def _get_tenant_domain(slug):
    """ Accommodate for subfolders by just returning the slug."""
    
    if hasattr(settings, 'TENANT_SUBFOLDER_PREFIX'):
        return slug
    return '{0}.{1}'.format(slug, settings.TENANT_USERS_DOMAIN)


@pytest.mark.django_db()
def test_provision_tenant_inactive_user(tenant_user):
    """Test tenant creation with inactive user."""
    tenant_user.is_active = False
    tenant_user.save()

    with pytest.raises(InactiveError, match='Inactive user passed'):
        tasks.provision_tenant(
            'inactive_test',
            'inactive_test',
            tenant_user.email,
        )


@pytest.mark.django_db()
def test_duplicate_tenant_url(test_tenants, tenant_user):
    """Tests duplicate URL error."""
    # Get first non-public tenant to use
    slug = test_tenants.first().slug

    with pytest.raises(ExistsError, match='URL already exists'):
        tasks.provision_tenant(slug, slug, tenant_user.email)
