import tempfile
from pathlib import Path

import pytest

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.builder import WebserviceBuilder


def test_builder_with_all_operations():
    """Test builder creates webservice with all operations enabled."""
    builder = WebserviceBuilder(name="TestService")
    builder.enable_operations(TicketOperation.CREATE, TicketOperation.GET,
                              TicketOperation.SEARCH, TicketOperation.UPDATE)
    config = builder.build()

    operations = config["Provider"]["Operation"]
    assert len(operations) == 4
    assert all(op in operations for op in ["ticket-create", "ticket-get", "ticket-search", "ticket-update"])


def test_builder_with_user_restriction():
    """Test builder applies user restriction correctly."""
    config = (WebserviceBuilder(name="TestService")
              .enable_operations(TicketOperation.CREATE)
              .set_restricted_by("test-user")
              .build())

    assert "Restricted to user 'test-user'" in config["Description"]


def test_builder_without_user_restriction():
    """Test builder works without user restriction."""
    config = (WebserviceBuilder(name="TestService")
              .enable_operations(TicketOperation.CREATE)
              .build())

    assert "Restricted to user" not in config["Description"]


def test_builder_saves_to_yaml():
    """Test builder saves configuration to YAML file."""
    builder = WebserviceBuilder(name="TestService")
    builder.enable_operations(TicketOperation.CREATE, TicketOperation.GET)
    config = builder.build()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "TestService.yml"
        builder.save_to_file(config, file_path)

        assert file_path.exists()
        content = file_path.read_text(encoding='utf-8')
        assert all(s in content for s in ["Provider:", "Operation:", "ticket-create:", "ticket-get:"])


def test_builder_raises_error_without_operations():
    """Test builder raises error when no operations enabled."""
    with pytest.raises(ValueError, match="No operations have been enabled"):
        WebserviceBuilder(name="TestService").build()


def test_bootstrap_pattern():
    """Test exact bootstrap.py usage pattern."""
    builder = WebserviceBuilder(name="BootstrapService")
    builder.enable_operations(TicketOperation.CREATE, TicketOperation.GET,
                              TicketOperation.SEARCH, TicketOperation.UPDATE)
    builder.set_restricted_by("bootstrap-user")
    config = builder.build()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "BootstrapService.yml"
        builder.save_to_file(config, file_path)

        assert len(config["Provider"]["Operation"]) == 4
        assert file_path.exists()
        assert file_path.stat().st_size > 1000


def test_builder_transport_config():
    """Test builder creates proper transport and route configuration."""
    config = (WebserviceBuilder(name="TestService")
              .enable_operations(TicketOperation.CREATE, TicketOperation.GET)
              .build())

    transport = config["Provider"]["Transport"]
    assert transport["Type"] == "HTTP::REST"

    routes = transport["Config"]["RouteOperationMapping"]
    assert routes["ticket-create"]["Route"] == "/tickets"
    assert routes["ticket-get"]["Route"] == "/tickets/:TicketId"
    assert "FrameworkVersion" in config
