"""
This module is used to modify SETTINGS during tests.

All defined fixtures should include settings()
"""

import pytest


@pytest.fixture(autouse=True)
def _password_hashers(settings) -> None:
    """Forces django to use fast password hashers for tests."""
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]


@pytest.fixture(autouse=True)
def _debug(settings) -> None:
    """Sets proper DEBUG and TEMPLATE debug mode for coverage."""
    settings.DEBUG = False
    for template in settings.TEMPLATES:
        template['OPTIONS']['debug'] = True


@pytest.fixture(autouse=False)
def tenant_type_settings(settings):
    settings.HAS_MULTI_TYPE_TENANTS = True
    settings.MULTI_TYPE_DATABASE_FIELD = "tenant_type"

    settings.TENANT_MODEL = 'companies.CompanyWithType'
    settings.TENANT_DOMAIN_MODEL = 'companies.DomainWithType'

    settings.TENANT_TYPES = {
        "public": {
            "APPS": [
                'django_tenants',
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'tenant_users.permissions',
                'tenant_users.tenants',
                'django_test_app.companies',
                'django_test_app.users',
            ]
        },
        "example_type": {
            "APPS": [
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'tenant_users.permissions',
            ]
        },
    }
    apps = []
    for schema in settings.TENANT_TYPES:
        apps += [
            app for app in settings.TENANT_TYPES[schema]["APPS"] if app not in apps
        ]
    settings.INSTALLED_APPS = apps
    # YourModel.add_to_class('dynamic_field', models.CharField(max_length=100))
