# Version history

We follow [Semantic Versions](https://semver.org/) starting at the `0.4.0` release.

## 1.4.0 (2024-05-06)

### Features
* Added management command for simple use of create_public_tenant by @jgentil in [#565](https://github.com/Corvia/django-tenant-users/pull/565)
* Adds support for Django 5.0 and Python 3.12
* Drops support for Django 3.2 and Python 3.7

### Misc

* Correct function reference in 'using' page by @Dresdn in [#532](https://github.com/Corvia/django-tenant-users/pull/532)
* Implement Ruff by @Dresdn in [#535](https://github.com/Corvia/django-tenant-users/pull/535)


## 1.3.0 (2023-11-14)

### Features

- Added support for multi-tenant types by @Wizely99 in [#475](https://github.com/Corvia/django-tenant-users/pull/475)

### Misc

- Major redesign of docs

## 1.2.0 (2023-08-08)

### Features

- Adds support for Django 4.2

### Fixes

- Used pk instead of id for universal access by @ysidromdenis [#355](https://github.com/Corvia/django-tenant-users/pull/357)

## 1.1.1 (2022-11-26)

### Misc

- Remove deprecation warning regarding default_app_config for django >= 3.2 [#326](https://github.com/Corvia/django-tenant-users/pull/326)
- Add Django 4.1 to PyPi Trove classifiers list
- Update downstream dependencies to latest versions

## 1.1.0 (2022-10-01)

### Features

- Adds support for Django 4.2
- Drops support for Django 2.2

### Misc

- There is now a direct dependency on django-tenants and support versions of Django (2.2, 3.2, 4.0, and 4.1)
- Updates downstream dependencies

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
- Topic hyperlinks on readme fixed

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
