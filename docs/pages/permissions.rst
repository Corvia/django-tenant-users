#######################
 Permissions Reference
#######################

**********************
 Permission Utilities
**********************

``django-tenant-users`` offers utility functions to manage permissions
across tenants. These functions provide fine-grained control over user
roles and access within each tenant.

.. autoclass:: tenant_users.permissions.models.PermissionsMixinFacade
   :members:
   :undoc-members:
   :show-inheritance:

*******************
 Permission Models
*******************

The permission models in ``django-tenant-users`` extend Django's
built-in permissions framework. This extension allows for the definition
of tenant-specific roles and permissions, ensuring that each tenant has
its own set of access controls.

.. autoclass:: tenant_users.permissions.models.UserTenantPermissions
   :members:
   :undoc-members:
   :show-inheritance:

.. note::

   The ``UserTenantPermissions`` model includes ``created_at`` and
   ``modified_at`` timestamp fields for tracking when users join tenants
   and when their permissions change.
