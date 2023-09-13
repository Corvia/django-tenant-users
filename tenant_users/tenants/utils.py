from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import (
    get_multi_type_database_field_name,
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    get_tenant_types,
    has_multi_type_tenants,
)

from tenant_users.tenants.models import ExistsError, SchemaError


def get_current_tenant():
    current_schema = connection.schema_name
    TenantModel = get_tenant_model()
    tenant = TenantModel.objects.get(schema_name=current_schema)
    return tenant


def create_public_tenant(
    domain_url,
    owner_email,
    is_superuser=False,
    is_staff=False,
    tenant_extra_data={},
    **owner_extra,
):
    """Create a public tenant with an owner user.

    `**Creates**` a public tenant in a multi-tenant architecture, `**assigns**` an owner user to it, and `**sets**` the owner's password as unusable if not provided.

    **Args**
    * `domain_url (str)`: The domain URL for the public tenant.
    * `owner_email (str)`: The email address of the owner user.
    * `is_staff`: Whether the user is  allowed to enter the admin panel. Defaults to `False`.
    * `is_superuser`:Whether the user has all permissions in the respective tenant. Defaults to `True`.
    * `tenant_extra_data`: Additional attributes for the tenant model (e.g., paid_until, on_trial,location,vision e.t.c).
    * `owner_extra`: Additional attributes for the owner user (e.g., first_name, last_name).

    **Returns:**

    * `Tuple[YourTenantModel, YourDomainModel, YourUserModel]`: A tuple containing the created public tenant, its domain, and the owner user.
    """

    UserModel = get_user_model()
    TenantModel = get_tenant_model()
    public_schema_name = get_public_schema_name()

    if TenantModel.objects.filter(schema_name=public_schema_name).first():
        raise ExistsError("Public tenant already exists")

    # Create public tenant user. This user doesn't go through object manager
    # create_user function because public tenant does not exist yet
    profile = UserModel.objects.create(
        email=owner_email,
        is_active=True,
        **owner_extra,
    )

    # Create the public tenant
    if has_multi_type_tenants():
        valid_tenant_types = get_tenant_types()
        tenant_type = public_schema_name

        # Check if the specified tenant type is valid
        if tenant_type not in valid_tenant_types:
            valid_type_str = ', '.join(valid_tenant_types)
            error_message = "{} is not a valid tenant type. Choices are {}.".format(
                tenant_type, valid_type_str
            )
            raise SchemaError(error_message)

        tenant_extra_data.update({get_multi_type_database_field_name(): tenant_type})

    public_tenant = TenantModel.objects.create(
        schema_name=public_schema_name,
        name="Public Tenant",
        owner=profile,
        **tenant_extra_data,
    )

    # Add one or more domains for the tenant
    domain = get_tenant_domain_model().objects.create(
        domain=domain_url,
        tenant=public_tenant,
        is_primary=True,
    )

    # Add system user to public tenant (no permissions)
    public_tenant.add_user(profile, is_superuser=is_superuser, is_staff=is_staff)

    # Handle setting the password for the user
    if 'password' in owner_extra:
        profile.set_password(owner_extra['password'])
    else:
        profile.set_unusable_password()
    profile.save()

    return public_tenant, domain, profile
