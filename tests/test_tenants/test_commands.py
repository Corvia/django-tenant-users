from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from tenant_users.tenants.models import ExistsError

DOMAIN_URL = "example.net"
OWNER_EMAIL = "example@example.net"
ERROR_MSG = "Schema Exists"


def test_create_public_tenant_command_success():
    out = StringIO()

    with patch(
        "tenant_users.tenants.management.commands.create_public_tenant.create_public_tenant"
    ) as mocked_cpt:
        call_command(
            "create_public_tenant",
            stdout=out,
            domain_url=DOMAIN_URL,
            owner_email=OWNER_EMAIL,
        )

    mocked_cpt.assert_called_once_with(domain_url=DOMAIN_URL, owner_email=OWNER_EMAIL)
    out_value = out.getvalue()
    assert DOMAIN_URL in out_value
    assert OWNER_EMAIL in out_value
    assert "Successfully created public tenant" in out_value


def test_create_public_tenant_command_failure():
    out = StringIO()

    with patch(
        "tenant_users.tenants.management.commands.create_public_tenant.create_public_tenant",
        side_effect=ExistsError(ERROR_MSG),
    ) as mocked_cpt:
        call_command(
            "create_public_tenant",
            stdout=out,
            domain_url=DOMAIN_URL,
            owner_email=OWNER_EMAIL,
        )

    mocked_cpt.assert_called_once_with(domain_url=DOMAIN_URL, owner_email=OWNER_EMAIL)
    out_value = out.getvalue()
    assert ERROR_MSG in out_value
    assert "Error creating public tenant" in out_value
