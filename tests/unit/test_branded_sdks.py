import pytest

from otobo import OTOBOClient, OTOBOError, TicketOperation
from otobo_znuny.clients.otobo_client import OTOBOZnunyClient
from otobo_znuny_python_client import OTOBOZnunyClient as LegacyClient
from otrs_gi_core.clients.generic_interface_client import GenericInterfaceClient
from znuny import ZnunyClient, ZnunyError


@pytest.mark.unit
def test_otobo_public_imports():
    assert OTOBOClient is GenericInterfaceClient
    assert OTOBOError.__name__ == "GenericInterfaceError"


@pytest.mark.unit
def test_znuny_public_imports():
    assert ZnunyClient is GenericInterfaceClient
    assert ZnunyError.__name__ == "GenericInterfaceError"


@pytest.mark.unit
def test_compatibility_imports():
    assert OTOBOZnunyClient is GenericInterfaceClient
    assert LegacyClient is GenericInterfaceClient
    assert TicketOperation.CREATE.value == "TicketCreate"


@pytest.mark.unit
def test_branded_cli_apps_exist():
    import otobo.cli as otobo_cli
    import znuny.cli as znuny_cli

    assert hasattr(otobo_cli, "app")
    assert hasattr(otobo_cli, "run")
    assert hasattr(znuny_cli, "app")
    assert hasattr(znuny_cli, "run")
