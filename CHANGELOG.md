# Version history

We follow [Semantic Versions](https://semver.org/) starting at the `0.4.0` release.

## {{ Next Version }}

## 1.0.0 (2022-02-09)

### Breaking Changes

- Support for [django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas) has been removed due to last release being in 2017
- Removed `tenant_users.compat` module as you can now directly import from `django_tenants.utils`

### Features

- Adds `settings.TENANT_SUBFOLDER_PREFIX` support from `django_tenants` [#85](https://github.com/Corvia/django-tenant-users/issues/85)
- Adds support for Django 4.0 [#158](https://github.com/Corvia/django-tenant-users/issues/158)
- Drops `django 3.1` support
- Drops `python 3.6` support

### Bug Fixes

- Fixes string representation of `UserTenantPermissions` object [#84](https://github.com/Corvia/django-tenant-users/issues/84)

### Misc

- Testing has been simplified to a single test project
- Moves to Github Actions strategy.matrix

## 0.4.0 (2021-10-14)

### Bug Fixes

- Replace deprecated `connection.get_schema()` with `connection.schema_name`

### Features

- Adds `python3.7`, `python3.8`, `python3.9` support
- Adds `django2.2`, `django3.1`, `django3.2` support
- Drops `python3.5` support
- Drops `django1.11` support

### Improvements

- Implemented `tenant_cached_property` to reduce number of queries for user permissions
- Adds CHANGELOG
- Moves to `poetry`
- Adds initial set of tests
- Use `nox` for testing
- Adds `mypy` support
- Adds `black` and `wemake-python-styleguide` support
- Refactored test project into one project per framework

(Anything before 0.4.0 was not recorded.)
