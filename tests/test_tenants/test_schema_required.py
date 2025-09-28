import pytest
from django.db import connection
from django_tenants.utils import get_public_schema_name


@pytest.mark.django_db
def test_schema_required_restores_connection_state(
    public_tenant, create_tenant, tenant_user
) -> None:
    """Test that @schema_required properly restores connection state.

    This test verifies that the @schema_required decorator correctly restores
    both connection.schema_name and connection.tenant to their original values
    after executing a method that temporarily switches to a tenant schema.

    The test:
    1. Starts in the public schema context
    2. Records the initial connection state
    3. Calls a @schema_required decorated method on a tenant
    4. Verifies the connection state is properly restored

    This test will FAIL until the @schema_required decorator is fixed to
    properly manage connection.tenant state.
    """
    # Start in public tenant context
    public_tenant.activate()

    # Verify we're starting in the public schema
    assert connection.schema_name == get_public_schema_name()  # type: ignore[attr-defined]
    initial_schema_name = connection.schema_name  # type: ignore[attr-defined]
    initial_tenant = getattr(connection, "tenant", None)

    # Create a test tenant
    test_tenant = create_tenant(tenant_user, "test_schema_required")

    result = test_tenant.test_schema_method()

    expected_result = f"Called on tenant: {test_tenant.schema_name}"
    assert result == expected_result, (
        f"Method did not execute correctly. Expected: {expected_result}, got: {result}"
    )

    # Verify connection state is fully restored
    assert connection.schema_name == initial_schema_name, (  # type: ignore[attr-defined]
        f"Expected: {initial_schema_name}, got: {connection.schema_name}"  # type: ignore[attr-defined]
    )

    current_tenant = getattr(connection, "tenant", None)
    assert current_tenant == initial_tenant, (
        f"Expected: {initial_tenant}, got: {current_tenant}"
    )
