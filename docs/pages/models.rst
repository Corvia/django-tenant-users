##################
 Models Reference
##################

The ``django-tenant-users`` extension introduces specialized models to
handle multi-tenancy in Django applications. This page delves into the
intricacies of these models, providing insights and examples to help
developers integrate and customize them effectively.

******************
 TenantBase Model
******************

The ``TenantBase`` model is central to the multi-tenancy architecture.
It represents each individual tenant or client within your application.

.. autoclass:: tenant_users.tenants.models.TenantBase
   :members:
   :undoc-members:
   :show-inheritance:

************
 User Model
************

The ``User`` model in ``django-tenant-users`` is tailored to support
multi-tenancy. While each user is primarily associated with a specific
tenant, ensuring data isolation, the architecture also supports global
users that can span multiple tenants.

.. autoclass:: tenant_users.tenants.models.UserProfile
   :members:
   :undoc-members:
   :show-inheritance:

*********************
 UserProfile Manager
*********************

The ``UserProfileManager`` is a custom manager for the ``UserProfile``
model. This provides additional methods and utilities for user-related
operations.

.. autoclass:: tenant_users.tenants.models.UserProfileManager
   :members:
   :undoc-members:
   :show-inheritance:
