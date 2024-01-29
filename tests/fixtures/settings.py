"""This module is used to modify SETTINGS during tests.

All defined fixtures should include settings()
"""

import pytest


@pytest.fixture(autouse=True)
def _password_hashers(settings) -> None:
    """Forces django to use fast password hashers for tests."""
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]


@pytest.fixture(autouse=True)
def _debug(settings) -> None:
    """Sets proper DEBUG and TEMPLATE debug mode for coverage."""
    settings.DEBUG = False
    for template in settings.TEMPLATES:
        template["OPTIONS"]["debug"] = True


@pytest.fixture(autouse=False)
def _tenant_type_settings(settings):
    settings.HAS_MULTI_TYPE_TENANTS = True
    settings.MULTI_TYPE_DATABASE_FIELD = "type"
    delattr(settings, "SHARED_APPS")
    delattr(settings, "TENANT_APPS")

    tenant_types = {
        "public": {
            "APPS": [
                "django_tenants",
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "tenant_users.permissions",
                "tenant_users.tenants",
                "django_test_app.companies",
                "django_test_app.users",
            ],
        },
        "type2": {
            "APPS": [
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "tenant_users.permissions",
            ],
        },
    }

    settings.TENANT_TYPES = tenant_types

    installed_apps = []
    for schema in tenant_types:
        installed_apps += [
            app for app in tenant_types[schema]["APPS"] if app not in installed_apps
        ]

    settings.INSTALLED_APPS = installed_apps
