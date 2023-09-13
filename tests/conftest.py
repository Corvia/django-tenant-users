"""
This module is used to provide configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""

pytest_plugins = [
    "tests.fixtures.db",
    "tests.fixtures.settings",
    "tests.fixtures.tenant",
]
