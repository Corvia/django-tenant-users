#####################
 django-tenant-users
#####################

.. image:: https://github.com/Corvia/django-tenant-users/actions/workflows/test.yml/badge.svg
   :alt: Build Status
   :target: https://github.com/Corvia/django-tenant-users/actions/workflows/test.yml

.. image:: https://codecov.io/gh/Corvia/django-tenant-users/branch/master/graph/badge.svg?token=PRS5HhOYPl
   :alt: codecov
   :target: https://codecov.io/gh/Corvia/django-tenant-users

.. image:: https://img.shields.io/pypi/v/django-tenant-users.svg?maxAge=180
   :alt: PyPI Package
   :target: https://pypi.org/project/django-tenant-users/

.. image:: https://img.shields.io/pypi/pyversions/django-tenant-users.svg?maxAge=180
   :alt: Python Versions
   :target: https://pypi.org/project/django-tenant-users/

.. image:: https://img.shields.io/pypi/djversions/django-tenant-users.svg?maxAge=180
   :alt: Django Versions
   :target: https://pypi.org/project/django-tenant-users/

.. image:: https://img.shields.io/pypi/dm/django-tenant-users.svg?maxAge=180
   :alt: PyPI Monthly Downloads
   :target: https://pypi.org/project/django-tenant-users/

Welcome to ``django-tenant-users``, the sidekick to ``django-tenants``
that sorts out user management in a multi-tenant Django world. 🚀

**********
 Overview
**********

Building on the solid foundation of ``django-tenants``,
``django-tenant-users`` focuses on the nuances of user management across
tenants. It ensures users can authenticate globally but have permissions
tailored to each specific tenant. In essence, it's the bridge that sorts
out the user stuff in a multi-tenant setup.

🔍 **Key Features**:

-  **Global Authentication with Tenant-Specific Permissions**:
   Authenticate once, act based on tenant rules.
-  **Distinct Schema Permissions**: Separate permissions for each tenant
   a user belongs to.
-  **Seamless Integration**: Works harmoniously with Django's built-in
   user and permissions frameworks.

*****************
 Getting Started
*****************

#. **Installation**: Dive into our `Installation Guide
   <https://django-tenant-users.rtfd.io/en/latest/pages/installation.html>`_
   to get ``django-tenant-users`` up and running.

#. **Usage**: Check out the `Using Guide
   <https://django-tenant-users.rtfd.io/en/latest/pages/using.html>`_ to
   see how to make the most of the package.

#. **Core Concepts**: If you're curious about the ideas driving our
   design, the `Core Concepts
   <https://django-tenant-users.rtfd.io/en/latest/pages/concepts.html>`_
   page is a great place to start.

************
 Contribute
************

We ❤️ contributions! Whether it's a bug report, a new feature, or
feedback on the project, we'd love to hear from you.

*********
 License
*********

``django-tenant-users`` is open-source and is licensed under the `MIT
License
<https://raw.githubusercontent.com/Corvia/django-tenant-users/master/LICENSE>`_.
