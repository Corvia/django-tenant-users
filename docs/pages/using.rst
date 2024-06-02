Using django-tenant-users
=========================

After installing and configuring ``django-tenant-users``, here's what you need to know
to get started.


Provisioning a New Tenant
-------------------------

To set up a new tenant in your application, utilize
:func:`tasks.create_public_tenant() <tenant_users.tenants.tasks.provision_tenant>`:

.. code-block:: python

   from tenant_users.tenants.tasks import provision_tenant
   from users.models import TenantUser
   provision_tenant_owner=CustomUserModel.objects.get(email="admin@evilcorp.com")


   tenant,domain = provision_tenant("EvilCorp", "evilcorp",provision_tenant_owner)


Using Multi-Type Tenants
~~~~~~~~~~~~~~~~~~~~~~~~

If you're leveraging the `Multi-type Tenants feature <https://django-tenants.readthedocs.io/en/latest/use.html#multi-types-tenants>`_
from ``django-tenants``, use the ``tenant_type`` keyword when calling the
:func:`utils.create_public_tenant() <tenant_users.tenants.tasks.provision_tenant>`
function:

.. code-block:: python

   from tenant_users.tenants.tasks import provision_tenant
   from users.models import TenantUser

   provision_tenant_owner = TenantUser.objects.get(email="admin@evilcorp.com")

   tenant, domain = provision_tenant(
      "EvilCorp", "evilcorp", provision_tenant_owner, tenant_type="tenant_type"
   )

.. note::
   Provisioning creates a new schema. Handle this asynchronously, e.g., with Celery.


Creating a User
---------------
Create users through the object manager:

.. code-block:: python

   from users.models import TenantUser

   user = TenantUser.objects.create_user("user@evilcorp.com", "password", True)

.. note::
   In django-tenant-users, emails are usernames.


Deletion Mechanism
------------------
Instead of permanently deleting users and tenants, ``django-tenant-users`` opts for
marking them as inactive. This approach ensures data integrity and allows for potential
reactivation in the future.


Delete Tenants
~~~~~~~~~~~~~~

The proper way to delete a tenant is to use the manager method:

.. code-block:: python

   from companies.models import Company

   evil = Company.objects.get(slug='evil')
   evil.delete_tenant()


Delete Users
~~~~~~~~~~~~

The proper way to delete a user in ``django-tenant-users`` is to use the manager method:

.. code-block:: python

   from users.models import TenantUser

   user = TenantUser.objects.get(email='user@domain.com')
   TenantUser.objects.delete_user(user)


Tenant/User Management
----------------------

To give a user access to a tenant, simply use the
:func:`TenantBase.add_user() <tenant_users.tenants.models.TenantBase.add_user>`
function.

.. code-block:: python

   from companies.models import Company
   from users.models import TenantUser

   user = TenantUser.objects.get(email='user@domain.com')
   evil = Company.objects.get(slug='evil')
   evil.add_user(user)


Utilities and Helper Functions
------------------------------
``django-tenant-users`` offers a variety of utilities and helpers for helping manage
your users and tenant permissions. See the :doc:`utilities` page for more information.
