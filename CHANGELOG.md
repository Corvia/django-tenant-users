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
