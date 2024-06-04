###############
 Core Concepts
###############

Understanding the foundational concepts behind ``django-tenant-users``
can help you make the most of its features and contribute more
effectively to its development.

*****************************************
 TenantBase: Extending Tenant Management
*****************************************

``TenantBase`` builds upon the ``TenantMixin`` from ``django-tenants``
by adding additional features to enhance tenant management of user
permissions.

Key Additions in ``TenantBase``:

-  **Tenant Ownership**:
      Each tenant has an associated owner.

-  **User Management Methods**:
      Functions to add or remove users from a tenant.

-  **Ownership Transfer**:
      Utilities to change the owner of a tenant.

-  **Deletion Mechanism**:
      Instead of outright deletion, tenants are handled to maintain data
      integrity. Refer to the deletion section for more details.

**********************************
 The Need for a Custom User Model
**********************************

In multi-tenancy applications, a single user might need to interact with
multiple tenants. To facilitate this, ``django-tenant-users`` requires a
custom user model that can associate users with specific tenants while
maintaining a global authentication mechanism. This design ensures data
isolation at the tenant level while providing a seamless authentication
experience.

********************************************
 Custom Authentication Backend: UserBackend
********************************************

The ``UserBackend`` class in ``django-tenant-users`` is designed to
handle user authentication across multiple tenants. While it ensures
global-level authentication, it also maintains tenant-specific data for
each user. This backend leverages ``UserProfile`` for authentication and
``UserTenantPermissions`` for authorization. The magic behind this
functionality lies in the facade classes, which direct requests to the
appropriate locations.

*************************************
 Handling User and Tenant "Deletion"
*************************************

In ``django-tenant-users``, we've adopted a strategy to preserve data
integrity while still giving the appearance of deletion to end-users.
Here's how we manage the "deletion" of users and tenants:

-  **User "Deletion"**:
      -  Instead of permanently removing a user, we set their
         ``is_active``, ``is_staff``, and ``is_superuser`` attributes to
         ``False``.

      -  We disassociate the user from any tenants they own and remove
         all their permissions across all associated tenants.

-  **Tenant "Deletion"**:
      -  A tenant can be "deleted" either manually by a user or
         automatically if a "deleted" user owns it.

      -  During "deletion", we disassociate all users from the tenant
         and transfer the ownership of the tenant's schema to the public
         schema's owner.

      -  The tenant's URL is renamed to a format like
         ``ownerid-timestamp-originalurl``. This retains some history of
         the tenant's ownership and also frees up the URL for future
         use.

-  **Unique Schema Naming**:
      -  To avoid conflicts at the database schema level, every tenant's
         schema name is appended with a timestamp (seconds since the
         epoch). This ensures each schema is unique.

This approach ensures that while users and tenants might seem "deleted"
from an operational perspective, the underlying data remains intact,
allowing for potential recovery or analysis in the future.
