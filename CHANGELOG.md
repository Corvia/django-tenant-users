# Version history

We follow [Semantic Versions](https://semver.org/) starting at the `0.4.0` release.

## Unreleased

### Features

* Add `domain_extra_data` support to tenant provisioning utilities (`provision_tenant`, `create_public_tenant`) to pass extra fields to domain creation

### Deprecations

* Deprecate passing arbitrary `**kwargs` as owner fields to `create_public_tenant`; use `owner_extra_data={...}` instead, with a warning emitted when using the deprecated method (which still works as before for now)

## 2.2.1 (2025-10-07)

## What's Changed
* Fix mypy internal error with generic type inheritance in [#871](https://github.com/Corvia/django-tenant-users/pull/871)

## 2.2.0 (2025-10-06)

### Features

* Add configurable queryset optimization for tenant permissions via `TENANT_USERS_PERMS_QUERYSET` setting to reduce N+1 queries when accessing related data (profile, groups, etc.)
* Add built-in `get_optimized_tenant_perms_queryset()` utility function in `tenant_users.permissions.utils` for common optimization use cases
* Add `created_at` and `modified_at` timestamp fields to `UserTenantPermissions` for tracking when users join tenants and when their permissions change

## 2.1.3 (2025-09-23)

## What's Changed
* Fix: schema_required decorator connection state restoration in [#860](https://github.com/Corvia/django-tenant-users/pull/860)

## 2.1.2 (2025-09-12)

## What's Changed
* Fix: resolve UserTenantPermissions caching bug in remove_user in [#848](https://github.com/Corvia/django-tenant-users/pull/848)

## 2.1.1 (2025-04-08)

## What's Changed
* adds `is_authenticated` proxy property to `AbstractBaseUserFacade` by @nikatlas in [#755](https://github.com/Corvia/django-tenant-users/pull/755)

## 2.1.0 (2025-02-01)

## What's Changed
* added support for primary keys where the field id is missing in [#707](https://github.com/Corvia/django-tenant-users/issues/707) by @Jed-Giblin in [#708](https://github.com/Corvia/django-tenant-users/pull/708)
* Fix: security risk in `tenant_cached_property` with malicious schema names by @scur-iolus in [#709](https://github.com/Corvia/django-tenant-users/pull/709)
* Improve data consistency and prevent orphaned records in user/tenant management by @scur-iolus in [#732](https://github.com/Corvia/django-tenant-users/pull/732)



## 2.0.0 (2024-09-09) Breaking changes

## What's Changed

* Now returning created tenant from provision_tenant utility function by @Wizely99 in https://github.com/Corvia/django-tenant-users/pull/607
* Remove nargs by @ihfazhillah in https://github.com/Corvia/django-tenant-users/pull/669
* Allow verbosity to be set when creating public tenant by @Dresdn in https://github.com/Corvia/django-tenant-users/pull/677


## 1.5.0 (2024-05-22)

### Features

* Create TenantAccessMiddleware to limit TenantUsers accessing Tenants they don't belong to by @Dresdn in [#594](https://github.com/Corvia/django-tenant-users/pull/594)

### Misc

* Update using.rst by @jansalvador in [#590](https://github.com/Corvia/django-tenant-users/pull/590)


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
