##############
 Installation
##############

***************
 Prerequisites
***************

-  A Django project set up and running.

-  ``django-tenants`` installed and configured. If you haven't done this
   yet, refer to the `django-tenants documentation
   <https://django-tenants.readthedocs.io>`_ for guidance.

********************************
 Installing django-tenant-users
********************************

To install ``django-tenant-users``, use your favorite package manager:

.. code:: bash

   pip install django-tenant-users

*********************************
 Configuring Your Django Project
*********************************

Modifying the Tenant Model
==========================

Your existing ``TenantModel``, which should be configured in
``settings.py``, needs to be updated to inherit from our ``TenantBase``
instead of ``TenantMixin``.

Here's an example of how to modify your existing TenantModel:

.. code:: python

   from tenant_users.tenants.models import TenantBase


   class Company(TenantBase):
       name = models.CharField(max_length=100)
       description = models.TextField(max_length=200)

Creating the User Model
=======================

If you haven't already defined a custom user model in your project,
you'll need to create one and have it inherit from ``UserProfile``. See
the `Django User Model documentation
<https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#extending-the-existing-user-model>`_
for more information.

In the example below, we define a ``TenantUser`` model within the
``users`` application:

.. code:: python

   from tenant_users.tenants.models import UserProfile


   class TenantUser(UserProfile):
       name = models.CharField(max_length=100)

Updating Settings
=================

Add the ``tenant_users`` apps to ``SHARED_APPS`` and ``TENANT_APPS``.

.. code:: python

   SHARED_APPS = [
       ...
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "tenant_users.permissions",
       "tenant_users.tenants",
       "companies",
       "users",
       ...
   ]

   TENANT_APPS = [
       ...
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "tenant_users.permissions",
       ...
   ]

Using Multi-Type Tenants
========================

If you're leveraging the `Multi-type Tenants feature
<https://django-tenants.readthedocs.io/en/latest/use.html#multi-types-tenants>`_
.. code-block:: python .. code-block:: python

   TENANT_TYPES = {
      "public": {
         "APPS": [
            "django.contrib.auth", "django.contrib.contenttypes",
            "tenant_users.permissions", "tenant_users.tenants",
            "companies", "users", # Add other apps as needed ],

         "URLCONF": "myproject.urls.public",

      },

      "type1": {
         "APPS": [
            "django.contrib.auth", "django.contrib.contenttypes",
            "tenant_users.permissions", # Add other apps as needed ], },

      # Add other tenant types as needed }

.. important::

   Ensure the app containing your ``TenantBase`` (``companies``) and
   ``TenantUser`` (``users``), are **only** in the ``SHARED_APPS`` list.

User Authentication
-------------------

Switch to the custom authentication backend:

.. code:: python

   AUTHENTICATION_BACKENDS = ("tenant_users.permissions.backend.UserBackend",)

Tenant Domain
-------------

When provisioning new tenants, we need to know what domain to when
provisioning new tenants.

.. code:: python

   TENANT_USERS_DOMAIN = "domain.com"

Custom Auth User Model
----------------------

Finally, ensure that you define or update the ``AUTH_USER_MODEL`` to
point to the model inherting ``TenantUser``.

.. code:: python

   AUTH_USER_MODEL = "users.TenantUser"

.. note::

   Ensure that ``settings.TENANT_MODEL`` is set correctly from your
   ``django-tenant`` installation.

Optional Settings
=================

Setting up Cross Domain Cookies
-------------------------------

To allow single sign-on across tenants:

.. code:: python

   SESSION_COOKIE_DOMAIN = ".domain.com"

.. warning::

   Ensure you understand the implications of using
   ``SESSION_COOKIE_DOMAIN``.

.. note::

   If using Django admin, consider ``admin multisite``. You should
   ensure the configuration is correct to avoid unauthorized model
   access.

Tenant Access Middleware
------------------------

To ensure users have access to the requested tenant, you can add the
``TenantAccessMiddleware`` to your Django project. This middleware
checks if the authenticated user has access to the tenant specified in
the request. If the user does not have access, a 404 error is raised.
Unauthenticated users are allowed to proceed.

1. Add the ``TenantAccessMiddleware`` to your ``MIDDLEWARE`` setting in
``settings.py`` after Django's ``AuthenticationMiddleware``:

.. code:: python

   MIDDLEWARE = [
       ...
       "django.contrib.auth.middleware.AuthenticationMiddleware",
       ...
       "tenant_users.tenants.middleware.TenantAccessMiddleware",
       ...
   ]

2. Optionally, customize the error message by setting
   ``TENANT_USERS_ACCESS_ERROR_MESSAGE`` in your ``settings.py```:

.. code:: python

   TENANT_USERS_ACCESS_ERROR_MESSAGE = "Custom access denied message."

.. note::

   To grant a user access to the tenant, use the
   :meth:`tenant.add_user()
   <tenant_users.tenants.models.TenantBase.add_user>` method to add the
   user to the tenant.

*************************
 Provision Public Tenant
*************************

When working with django-tenants, it's essential to have a public tenant
created using ``migrate_schemas``. If you haven't set up the public
tenant during the django-tenants installation, no problem.
``django-tenant-users`` provides a :func:`utils.create_public_tenant()
<tenant_users.tenants.utils.create_public_tenant>`, which takes care of
this for you.

.. code:: python

   from tenant_users.tenants.utils import create_public_tenant

   create_public_tenant(domain_url="public.domain.com", owner_email="admin@domain.com")

Or, alternatively, use the management command:

.. code:: bash

   manage.py create_public_tenant --domain_url public.domain.com --owner_email admin@domain.com

******
 Fin!
******

Congratulations on successfully setting up ``django-tenant-users``! With
the installation complete, you're now equipped to harness the power of
global authentication and authorization for your multi-tenancy Django
projects.

As you move forward, we recommend diving into the following sections to
gain a deeper understanding and make the most of
``django-tenant-users``:

-  :doc:`using`: Explore how get started with the core functionalities.
-  :doc:`concepts`: Enhance your understanding of the foundational
   principles behind ``django-tenant-users``.

Happy coding!
