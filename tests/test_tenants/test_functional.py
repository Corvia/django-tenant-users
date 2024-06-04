from unittest.mock import patch

import pytest
from django.db import connection
from django.utils.functional import cached_property

from tenant_users.permissions.functional import tenant_cached_property


class MockTenant:

    @tenant_cached_property
    def tenant_aware_cached_property(self):
        current_schema = connection.schema_name
        return f"aware {current_schema}"

    @cached_property
    def tenant_unaware_cached_property(self):
        current_schema = connection.schema_name
        return f"unaware {current_schema}"


def test_tenant_cached_property():
    instance = MockTenant()

    # Mock the schema name for the first access
    with patch.object(connection, "schema_name", "schema_one"):
        assert instance.tenant_aware_cached_property == "aware schema_one"
        assert instance.tenant_unaware_cached_property == "unaware schema_one"

    # Mock the schema name for a second schema
    with patch.object(connection, "schema_name", "schema_two"):
        assert instance.tenant_aware_cached_property == "aware schema_two"
        assert "tenant_aware_cached_property" in instance.__dict__["schema_two"]
        assert instance.tenant_unaware_cached_property == "unaware schema_one"
        with pytest.raises(KeyError) as exc_info:
            instance.__dict__["schema_two"]["tenant_unaware_cached_property"]

        assert str(exc_info.value) == "'tenant_unaware_cached_property'"
        assert (
            instance.__dict__["schema_two"]["tenant_aware_cached_property"]
            == "aware schema_two"
        )

    # Accessing again with the first schema to check caching
    with patch.object(connection, "schema_name", "schema_one"):
        assert instance.tenant_aware_cached_property == "aware schema_one"
        assert instance.tenant_unaware_cached_property == "unaware schema_one"

    # Accessing again with the second schema to check caching
    with patch.object(connection, "schema_name", "schema_two"):
        assert instance.tenant_aware_cached_property == "aware schema_two"
        assert instance.tenant_unaware_cached_property == "unaware schema_one"

    # Clear the cached property for a schema and test recalculation
    with patch.object(connection, "schema_name", "schema_two"):
        del instance.__dict__["schema_two"]["tenant_aware_cached_property"]
        assert instance.tenant_aware_cached_property == "aware schema_two"
        assert "tenant_aware_cached_property" in instance.__dict__["schema_two"]


def test_tenant_cached_property_instance_none():
    # When instance is None, the property descriptor itself should be returned
    assert isinstance(MockTenant.tenant_aware_cached_property, tenant_cached_property)
