###################################
 django-tenant-users Documentation
###################################

``django-tenant-users`` enhances `django-tenants
<https://django-tenants.readthedocs.io/>`_ by refining user management
in multi-tenancy setups. This application ensures users authenticate
globally while having permissions specific to each tenant.

******************************
 Why use django-tenant-users?
******************************

-  **Global Authentication**:

      Users can authenticate once and gain access to multiple tenants.
      This provides a streamlined login experience, eliminating the need
      for multiple account setups.

-  **Tenant-Specific Permissions**:

      Even though users can authenticate globally, their permissions are
      tailored to each specific tenant they interact with. This ensures
      that a user's actions are always in line with the specific rules
      and roles of each tenant, including specific permissions for the
      public tenant.

-  **Seamless Integration with Django**:

      ``django-tenant-users`` is designed to gel seamlessly with
      Django's built-in user and permissions frameworks.

**************
 Dependencies
**************

While ``django-tenant-users`` offers specialized user management for
multi-tenancy, it's built on the solid foundation of ``django-tenants``.
If you're new to ``django-tenants``, check out their `official
documentation <https://django-tenants.readthedocs.io/>`_ to get the full
picture.

###################
 Table of Contents
###################

.. toctree::
   :caption: Contents
   :maxdepth: 2

   pages/installation
   pages/using
   pages/concepts
   pages/models
   pages/permissions
   pages/utilities
   pages/conributing
