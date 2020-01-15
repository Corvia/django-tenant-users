===================
django-tenant-users
===================
.. image:: https://img.shields.io/pypi/v/django-tenant-users.svg?maxAge=180
.. image:: https://img.shields.io/pypi/dm/django-tenant-users.svg?maxAge=180

Table of Contents
=================

- `Overview <overview_>`_  
- `Installation <installation_>`_ 
- `Test Project <testproject_>`_ 
- `Basic Settings <basicsettings_>`_ 
- `Modifying the Tenant Model <tenantmodel_>`_ 
- `Creating the User Model <usermodel_>`_ 
- `Configuring the Authentication Backend <authbackend_>`_ 
- `Configuring Cross Domain Cookies <cookies_>`_ 
- `Creating a User <createuser_>`_ 
- `Provisioning a Tenant <provisioning_>`_ 
- `Migrating and Creating the Public Tenant <migrating_>`_ 
- `Creating a User <createuser_>`_ 

This application expands the django users and permissions frameworks to work alongside
django-tenant-schemas or django-tenants to allow global users with permissions on a per-tenant basis.
This allows a single user to belong to multiple tenants and permissions in each tenant, including allowing permissions in the public tenant. This app also adds support for querying all tenants a user belongs to.

.. _overview:

Overview
========

To simplify the use of Django's models and ORM layer, we need to isolate each tenant so we don't have to filter objects (queries) by tenant. Since we are using PostgreSQL we handle this by using a separate schema for each tenant. We use django-tenant-schemas or django-tenants to handle all of this. Using separate schemas per tenant provides a small layer of security, permissions isolation, and some performance benefits. On the flip side, we've now segregated the database completely on a per-tenant basis, and have no default support for global authentication. For instance, if one user belongs to multiple tenants they should not need to have multiple accounts and should not have to sign in multiple times (i.e. be forced to sign for each tenant). They also should be able to see all the tenants they belong to. By default, this is not possible with django-tenant-schemas or django-tenants so we have created a solution to this problem (described below).


The django middleware (django-tenant-schemas or django-tenants) handles the schema setting automatically on a per-request basis. It does this by looking at the subdomain that the request comes in on and maps that to a 'tenant'. No subdomain, or the 'www' subdomain map to a default 'public' tenant. In order for this mapping to work to a tenant, we have to create the tenant and the tenant's schema in the database.

We leverage the tenant schemas middleware to handle most of this transparently. However, to get global authentication (global user accounts) and per-tenant authorization (permissions) working we rely on some of the nuances of schemas.

A schema is quite similar to a search path on a file system "path1;path2;path3" that gets searched in order. If no model exists in the first schema then the next one is searched. If the model exists but is empty, it does not continue searching (a model was found). By default, the 'public' schema is always transparently appended to the end of the schema path whenever set_schema is called.

Global Authentication Solution
------------------------------

With this in mind, it's easy to see that we can create a users table at the global level in the public schema but NOT in the tenants schemas and the users table will still be searched and found, regardless of which tenant is selected. However, the problem is that we need to create our permissions on a per tenant basis, not at a global level. In fact, since the public schema also represents the website, the permissions for a user at the global level should only reflect the permissions for the website (i.e. can I post on the blog?). It's really an entirely different permission set at the public schema level that we need to support.

The difficulty comes in at the Django level. Luckily Django supports using a custom user model. However, internally, the way Django uses the model tightly couples aspects of the authentication (user/pass and profile) and authorization (permissions) together, despite each one of those aspects inheriting from a separate mixin (parent tree: see PermissionsMixin and AbstractUserBase classes). As an artifact of the coupling, the authentication/permissions backend, as well as other components, make the assumption that it is one one model in the database. The built in function get_user_model() returns the model that is configured as the user model (whether its the stock django user model or a custom user model). We handle this in a relatively simplistic way. First, we decouple the two components (user profile and user permissions) into UserProfile and UserTenantPermissions. We install the UserProfile only at the SHARED_APPs (public schema) level. We install the Permissions model at ALL levels -- SHARED_APPs and TENANT_APPs (both public schema, and per tenant schema). Then we 'facade' the two together (see AbstractBaseUserFacade and TenantPermissionsMixinFacade classes) to make each model look and behave like it encapsulates all of the functionality of a single unified user model. The part that makes it a little more tricky (and perhaps more clever) is that the two models that are linked at any point in time for a query is defined by the currently set schema. 

Let's look at an example. When accessing the website (via a request), the public schema is set (because its the public tenant), then the public Permissions model located in the public schema is what gets looked up by permissions queries, as well as the public user model (which is also located in the public schema). When a request comes in for a tenant, "EvilCorp" the EvilCorp schema is selected automatically via the middleware. However, remember that the schema set is really a search path that also contains the public schema appended to the end (see above). Thus, when a query comes in looking up permissions, it finds a permissions model INSIDE the EvilCorp tenant, and uses those permissions (rather than the model in the public schema), but when it looks up the UserProfile, nothing exists in the EvilCorp tenant schema so it falls back and searches the public schema and finds the UserProfile there. So essentially we end up 'glueing' these components together at run time for any given query using the schema search path.

Next, we have to create a custom authentication backend to handle the new user/permission model segregation. Luckily this is fairly easy and almost requires no changes since both our models provide facade interfaces to each other! We don't have to change any of the logic in the auth backend (in fact the permission caching still even works at a per-tenant level automagially!). The only change we make is slight, and that is the way the default backend uses get_user_model() to look up meta data about the user model. We just override methods using this functionality to change this behavior and force it to use the tenant permissions model for permissions meta work, instead of the user model thats returned from get_user_model().

Tenants are stored at the public schema level and are also what defines each tenant. Tenants and users are linked at the public level as well, so we can query a user and see what tenants it belongs to, or query a tenant and see what users are associated. However, the permissions of a user are defined inside the tenant's schema itself, so to view that data, we have to switch the schema over (normally this happens automatically, but in the case of wanting to view a users permissions on a public profile page, we would have to force set the schema (connection.set_schema('EvilCorp'), as defined in the Tenant model for that tenant). We also have to remember to set it back. Most use cases will not ever have to touch the schema setting directly.

User and Tenant 'Deletion'
---------------------------

With this solution, we also implement an alternative to avoid actually deleting users or tenants, so we need a way to make them disappear into the ether (from the users perspective) without conflict (i.e. don't allow a deleted tenant to permanently monopolize a tenant URL subdomain, and don't allow a users email to never be used again for signup). To handle the user delete, we just set the user is_active/staff/superuser to false and delete all links to any tenants it owns, as well as all instances of permissions it has in any tenant it was associated with. A user can "delete" a tenant manually, or in the case that a deleted user owns a tenant, we "delete" the tenant. When we "delete" a tenant, we disassociate any users with any permissions, and then change the owner of the tenant's schema to the public schema's owner (the same owner that was configured when create_public_tenant command was run). When we do this, we also rename the tenant's URL to be ownerid-timestamp-originalurl. Not only does this encapsulate some of the history of the tenant's ownership, but it also frees up the URL namespace. Also, we never have to worry about schemas in the database conflicting because when we generate a tenant's schema, we append the timestamp (in seconds since the epoch) to the name. Thus, every schema ends up unique when made, eliminating any schema level conflicts.

To do a full delete on Users/Tenants the delete methods can be overridden, or force_drop=True can be passed in to delete. 

.. _installation:

Installation
============
Assuming you already have django-tenant-schemas or django-tenants installed and configured, the first step is to install ``django-tenant-users``. 

.. code-block:: bash

    pip install django-tenant-users
    
.. _testproject:

Test Project
============

All of the following settings/configuration can be seen in the dtu_test_project located in the `GitHub repository <https://github.com/Corvia/django-tenant-users.git>`_

.. _basicsettings:

Basic Settings
==============

You'll have to make the following additions to the ``SHARED_APPS`` and ``TENANT_APPS` in your ``settings.py`` file.

.. code-block:: python

    SHARED_APPS=[
        # ...
        'django.contrib.auth', # Defined in both shared apps and tenant apps
        'django.contrib.contenttypes', # Defined in both shared apps and tenant apps
        'tenant_users.permissions', # Defined in both shared apps and tenant apps
        'tenant_users.tenants', # defined only in shared apps 
        'customers', # Custom defined app that contains the TenantModel. Must NOT exist in TENANT_APPS
        'users', # Custom app that contains the new User Model (see below). Must NOT exist in TENANT_APPS
        # ...
    ]

    TENANT_APPS=[
        # ...
        'django.contrib.auth', # Defined in both shared apps and tenant apps
        'django.contrib.contenttypes', # Defined in both shared apps and tenant apps
        'tenant_users.permissions', # Defined in both shared apps and tenant apps
        # ...
    ]

You will have to set the ``TENANT_USERS_DOMAIN`` setting to the domain hosting the tenants. This is utilized in provision_tenant to fill out the domain_url to match incoming requests.

.. code-block:: python

    TENANT_USERS_DOMAIN = "example.com"

.. _tenantmodel:

Modifying the Tenant Model
==========================

Next we need to modify the TenantModel, which you should already have configured in settings.py. We need to change the inerhitance chain to inherit from ``TenantBase`` (previously it was ``TenantMixin``). Below is an example TenantModel located in the 'customers' app that we installed above in the basic configuration section. Note. this 'customers' should ONLY be installed in the SHARED_APPs list.

.. code-block:: python

    # customers/model.py

    from tenant_users.tenants.models import TenantBase

    class Client(TenantBase):
        name = models.CharField(max_length=100)
        description = models.TextField(max_length=200)

The settings.py file entry should look like:

.. code-block:: python

    settings.py 

    TENANT_MODEL = 'customers.Client'

.. _usermodel:

Creating the User Model
=======================

Now we need to do the same thing to the User model. If you are not using a custom user model, then one needs to be built and configured in settings.py. The custom user model needs to inherit from the tenant_users UserProfile model. Additional fields can then be added to your custom user model, if desired. In this example, we will add the TenantUser model to the ``users`` application that we installed above in the basic configuration.

.. code-block:: python

    # users/models.py

    from tenant_users.tenants.models import UserProfile
    
    class TenantUser(UserProfile):
        name = models.CharField(
            _("Name"),
            max_length = 100,
            blank = True,
        )

The settings.py file entry would look like (see Django documentation for more details):

.. code-block:: python

    settings.py
    
    AUTH_USER_MODEL = 'users.TenantUser'

.. _authbackend:

Setting up the Authentication Backend
=====================================

At this point we now have all of the user, permissions, and tenant models configured. Because Django does not completely isolate authorization (permissions) from authentication (user/pass) we have to use a minimally modified authentication backend. Switch the authentication backend as follows:


.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'tenant_users.permissions.backend.UserBackend',
    )

Notes:
If you want to use django admin you will have to utilize admin multisite. Warning: if you set this up incorrectly you could expose access to models that users are not permitted to access (due to the schema search path being present, and falling through. See notes in code).  
You must reset migrations after updating the user model.  


.. _cookies:

Setting up cross domain cookies
===============================

Setting up cross domain cookies will allow a single sign on to access any of the tenants with the same session cookies. 

.. code-block:: python

    SESSION_COOKIE_DOMAIN = '.mydomain.com'

Warning: read the django documentation to understand the impacts of using ``SESSION_COOKIE_DOMAIN``

.. _createuser:

Creating a User
===============

All users apart from the first public tenant user (see `Migrating and Creating the Public Tenant <migrating_>`_ for creating the first public tenant user) should be created through the object manager.

.. code-block:: python
    
    user = TenantUser.objects.create_user(email="user@evilcorp.com", password='password', is_active=True)

Currently all users rely on an email for the username. 

.. _provisioning:

Provisioning a Tenant
======================

Here is an example to provision a tenant with the url "evilcorp.example.com". Note that we set the ``TENANT_USERS_DOMAIN`` above to example.com.

Note: the user with the specified email must exist before provisioning a tenant. That's because users can exist without a tenant, but a tenant can't exist without a user (owner).

.. code-block:: python

    from tenant_users.tenants.tasks import provision_tenant

    fqdn = provision_tenant("EvilCorp", "evilcorp", "admin@evilcorp.com").

Since provisioning a tenant also has to create the entire schema -- depending on the models installed, it can take a while. It is recommended that this does not occur in the request/response cycle. A good asynchronous option is to use a task runner like Celery (along with tenant-schemas-celery) to handle this.

.. _migrating:

Migrate and Create the Public Tenant
====================================

Django tenant schemas requires migrate_schemas to be called and a public tenant to be created. Here is an example of creating the public tenant along with a default 'system' tenant owner.


.. code-block:: python

    # Create public tenant user.
    from tenant_users.tenants.utils import create_public_tenant
    create_public_tenant("my.evilcorp.domain", "admin@evilcorp.com")
