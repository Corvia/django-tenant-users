"""
This module is used to interact with the Database during tests.

https://pytest-django.readthedocs.io/en/latest/database.html
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, TransactionTestCase
from django_tenants.utils import (
    get_public_schema_name,
    get_tenant_domain_model,
    get_tenant_model,
    schema_context,
)

from tenant_users.tenants.utils import create_public_tenant
from test_project.companies.models import Company

TEST_TENANT_NAME = 'test'


@pytest.fixture()
def db(request, django_db_setup, django_db_blocker):  # noqa: PT004
    """
    Django db fixture.

    Seeing as this has the same signature, it overrides the fixture in
    pytest_django.fixtures

    It doesn't support quite the same things, such as transactional tests or
    resetting of sequences.

    The way our setup works here, is that due to performance reasons we want
    to override this, and then create our public and test tenant, before
    entering into the `atomic` block that pytest and Django normally runs tests
    in - this way we only have to do the heavy work of migrating our schemas
    once every test run, rather than every test.
    """
    django_db_blocker.unblock()
    request.addfinalizer(django_db_blocker.restore)  # noqa: PT021

    # Create the public and the test tenant.
    # We do this right before the pre_setup so it doesn't
    # get axed by the atomic block()
    with schema_context(get_public_schema_name()):
        # Get or create the public tenant
        _get_or_create_public_tenant()

        # Get the User
        tenant_user = get_user_model().objects.get(email='test@test.com')

        # Get or create the test tenant
        tenant = _get_or_create_test_tenant(tenant_user)

    connection.set_tenant(tenant)

    # Here we distinguish between a transactional test or not (corresponding to
    # Django's TestCase or its TransactionTestCase. Some tests that create/drop
    # tenants can't be run inside an atomic block, so must be marked as
    # transactional.
    if 'transactional' in request.keywords:
        test_case = TransactionTestCase(methodName='__init__')
    else:
        # This performs the rest of the test in an atomic() block which will
        # roll back the changes.
        test_case = TestCase(methodName='__init__')

    test_case._pre_setup()  # type: ignore # noqa: WPS437
    # Post-teardown function here reverts the atomic blocks to leave the DB
    # in a fresh state.
    request.addfinalizer(
        test_case._post_teardown,  # type: ignore # noqa: WPS437, PT021
    )  # This rolls the atomic block back


def _get_or_create_public_tenant() -> Company:
    try:
        public_tenant = Company.objects.get(
            schema_name=get_public_schema_name(),
        )
    except Company.DoesNotExist:
        create_public_tenant('public.test.com', 'test@test.com')
        public_tenant = Company.objects.get(
            schema_name=get_public_schema_name(),
        )
    return public_tenant


def _get_or_create_test_tenant(tenant_user) -> Company:
    """Fixture that gives us a test_tenant if we need it."""
    try:
        tenant = Company.objects.get(schema_name=TEST_TENANT_NAME)
    except Company.DoesNotExist:
        tenant = get_tenant_model()(
            name='Test',
            slug=TEST_TENANT_NAME,
            schema_name=TEST_TENANT_NAME,
            owner=tenant_user,
        )
        tenant.save(
            verbosity=0,
        )  # This saves the tenant and creates the tenant schema.

        # Setup the domain
        get_tenant_domain_model().objects.create(
            domain='tenant.test.com',
            tenant=tenant,
            is_primary=True,
        )

    return tenant
