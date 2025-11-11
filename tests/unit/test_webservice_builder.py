import tempfile
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.builder import WebserviceBuilder
from otobo_znuny_python_client.setup.webservices.operations import SUPPORTED_OPERATION_SPECS


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
        content = file_path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)

        assert "Provider" in parsed and "Operation" in parsed["Provider"]
        assert set(parsed["Provider"]["Operation"].keys()) == {"ticket-create", "ticket-get"}


def test_builder_raises_error_without_operations():
    """Test builder raises error when no operations enabled."""
    with pytest.raises(ValueError):
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


def test_set_framework_version_override():
    """Framework version override should be reflected in the config."""
    config = (WebserviceBuilder(name="TestService")
              .set_framework_version("12.0.0")
              .enable_operations(TicketOperation.CREATE)
              .build())

    assert config["FrameworkVersion"] == "12.0.0"


def test_clear_restriction_removes_value_map():
    """Clearing a restriction removes the ValueMap from the inbound mapping."""
    config = (WebserviceBuilder(name="TestService")
              .set_restricted_by("user")
              .clear_restriction()
              .enable_operations(TicketOperation.CREATE)
              .build())

    inbound_mapping = config["Provider"]["Operation"]["ticket-create"]["MappingInbound"]
    assert "ValueMap" not in inbound_mapping["Config"]


def test_reset_operations_clears_enabled_operations():
    """reset_operations should remove all previously enabled operations."""
    builder = WebserviceBuilder(name="TestService")
    builder.enable_operation(TicketOperation.CREATE)
    builder.reset_operations()
    builder.enable_operation(TicketOperation.GET)
    config = builder.build()

    operations = config["Provider"]["Operation"]
    assert set(operations.keys()) == {"ticket-get"}


def test_enable_operation_validates_supported_operations():
    """Enabling an operation not present in operation_specs raises ValueError."""
    limited_specs = {TicketOperation.CREATE: SUPPORTED_OPERATION_SPECS[TicketOperation.CREATE]}
    builder = WebserviceBuilder(name="TestService", operation_specs=limited_specs)

    with pytest.raises(ValueError):
        builder.enable_operation(TicketOperation.SEARCH)

    # The supported operation can still be enabled and appears in the config.
    config = builder.enable_operation(TicketOperation.CREATE).build()
    assert set(config["Provider"]["Operation"].keys()) == {"ticket-create"}


def test_dump_yaml_avoids_aliases():
    """dump_yaml should list operations without emitting YAML alias markers."""
    builder = WebserviceBuilder(name="TestService")
    config = (builder
              .enable_operations(TicketOperation.CREATE, TicketOperation.UPDATE)
              .build())
    yaml_output = builder.dump_yaml(config)

    assert "ticket-create" in yaml_output
    assert "ticket-update" in yaml_output
    assert "&" not in yaml_output and "*" not in yaml_output

    parsed = yaml.safe_load(yaml_output)
    assert set(parsed["Provider"]["Operation"].keys()) == {"ticket-create", "ticket-update"}
