from unittest.mock import patch

import pytest
from django.db import connection
from django.utils.functional import cached_property

from tenant_users.constants import TENANT_CACHE_NAME
from tenant_users.permissions.functional import tenant_cached_property


class MockTenant:
    def __init__(self) -> None:
        self.call_count = 0

    @tenant_cached_property
    def tenant_aware_cached_property(self) -> str:
        self.call_count += 1
        current_schema = connection.schema_name  # type: ignore[attr-defined]
        return f"aware {current_schema}"

    @cached_property
    def tenant_unaware_cached_property(self) -> str:
        current_schema = connection.schema_name  # type: ignore[attr-defined]
        return f"unaware {current_schema}"


def test_tenant_cached_property_basic_behavior():
    """Test the basic behavior of tenant_cached_property with schema changes."""
    instance = MockTenant()

    # Mock the schema name for the first access
    with patch.object(connection, "schema_name", "schema_one"):
        assert instance.tenant_aware_cached_property == "aware schema_one"
        assert instance.tenant_unaware_cached_property == "unaware schema_one"

    cache = instance.__dict__[TENANT_CACHE_NAME]

    # Mock the schema name for a second schema (concurrent access)
    with patch.object(connection, "schema_name", "schema_two"):
        assert instance.tenant_aware_cached_property == "aware schema_two"
        assert "tenant_aware_cached_property" in cache["schema_two"]
        assert instance.tenant_unaware_cached_property == "unaware schema_one"
        with pytest.raises(KeyError) as exc_info:
            cache["schema_two"]["tenant_unaware_cached_property"]

        assert str(exc_info.value) == "'tenant_unaware_cached_property'"
        assert cache["schema_two"]["tenant_aware_cached_property"] == "aware schema_two"

    # Accessing again with the first schema to check caching
    with patch.object(connection, "schema_name", "schema_one"):
        assert instance.tenant_aware_cached_property == "aware schema_one"
        assert instance.tenant_unaware_cached_property == "unaware schema_one"

    # Accessing again with the second schema to check caching
    with patch.object(connection, "schema_name", "schema_two"):
        assert instance.tenant_aware_cached_property == "aware schema_two"
        assert instance.tenant_unaware_cached_property == "unaware schema_one"

    # Verify caching is isolated per schema
    assert "schema_one" in cache
    assert "schema_two" in cache


def test_tenant_cached_property_uses_a_dedicated_cache():
    """Test a dedicated cache is used for tenant-aware properties."""
    instance = MockTenant()

    assert TENANT_CACHE_NAME not in instance.__dict__

    with patch.object(connection, "schema_name", "schema_one"):
        assert instance.tenant_aware_cached_property == "aware schema_one"

    # The schema name should be a new key in our dedicated tenant cache dictionary
    assert "schema_one" not in instance.__dict__
    assert TENANT_CACHE_NAME in instance.__dict__
    assert "schema_one" in instance.__dict__[TENANT_CACHE_NAME]


def test_tenant_cached_property_value_is_not_recalculated():
    """Test resetting the cache for a specific tenant schema."""
    instance = MockTenant()

    with patch.object(connection, "schema_name", "my_schema"):
        assert instance.tenant_aware_cached_property == "aware my_schema"
        assert instance.call_count == 1

        # Another access should not trigger recalculation
        assert instance.tenant_aware_cached_property == "aware my_schema"
        assert instance.call_count == 1  # call count remains unchanged

        # Clear the cache and access the value again, should trigger recalculation
        cache = instance.__dict__[TENANT_CACHE_NAME]
        del cache["my_schema"]["tenant_aware_cached_property"]
        assert instance.tenant_aware_cached_property == "aware my_schema"
        assert "tenant_aware_cached_property" in cache["my_schema"]
        assert instance.call_count == 2  # call count is incremented


def test_tenant_cached_property_instance_none():
    """Test that the property descriptor itself is returned when instance is None."""
    assert isinstance(MockTenant.tenant_aware_cached_property, tenant_cached_property)
