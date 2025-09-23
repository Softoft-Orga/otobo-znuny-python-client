from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml
from typer.testing import CliRunner

# Ensure the legacy scripts import resolves to the package under src/otobo/scripts.
scripts_pkg = sys.modules.get("scripts")
if scripts_pkg is None:
    scripts_pkg = ModuleType("scripts")
    scripts_pkg.__path__ = []  # type: ignore[attr-defined]
    sys.modules["scripts"] = scripts_pkg

webservice_util = importlib.import_module("otobo.scripts.webservice_util")
setattr(scripts_pkg, "webservice_util", webservice_util)
sys.modules["scripts.webservice_util"] = webservice_util

from otobo.domain_models.ticket_operation import TicketOperation
from otobo.scripts import setup_webservices as sw


runner = CliRunner()


def _provider_name(self: sw.OperationSpec) -> str:
    return self.op.value


@pytest.fixture
def provider_name_property(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sw.OperationSpec,
        "provider_name",
        property(_provider_name),
        raising=False,
    )


def test_validate_name_accepts_valid_name() -> None:
    generator = sw.WebServiceGenerator()
    assert generator._validate_name("Valid_Name-123") == "Valid_Name-123"


def test_validate_name_rejects_empty() -> None:
    generator = sw.WebServiceGenerator()
    with pytest.raises(ValueError, match="cannot be empty"):
        generator._validate_name("")


def test_validate_name_rejects_invalid_characters() -> None:
    generator = sw.WebServiceGenerator()
    with pytest.raises(ValueError, match="Name must start"):
        generator._validate_name("1-invalid")


def test_description_for_restricted_user() -> None:
    generator = sw.WebServiceGenerator()
    description = generator._description("Service", "agent")
    assert description == "Webservice for 'Service'. Restricted to user 'agent'."


def test_description_for_all_agents() -> None:
    generator = sw.WebServiceGenerator()
    description = generator._description("Service", None)
    assert description == "Webservice for 'Service'. Accessible by all permitted agents."


def test_create_inbound_mapping_for_restricted_user() -> None:
    generator = sw.WebServiceGenerator()
    mapping = generator._create_inbound_mapping("restricted")
    expected = {
        "Type": "Simple",
        "Config": {
            "KeyMapDefault": generator._create_empty_mapping(),
            "KeyMapExact": {"UserLogin": "UserLogin"},
            "ValueMap": {"UserLogin": {"ValueMapRegEx": {".*": "restricted"}}},
            "ValueMapDefault": generator._create_empty_mapping(),
        },
    }
    assert mapping == expected


def test_create_inbound_mapping_when_unrestricted() -> None:
    generator = sw.WebServiceGenerator()
    mapping = generator._create_inbound_mapping(None)
    assert mapping == generator._create_simple_empty_mapping()


def test_generate_yaml_builds_expected_structure(provider_name_property: None) -> None:
    generator = sw.WebServiceGenerator()
    yaml_text = generator.generate_yaml(
        webservice_name="Service",
        enabled_operations=[TicketOperation.CREATE, TicketOperation.SEARCH],
        restricted_user="special",
        framework_version="12.0.0",
    )
    data = yaml.safe_load(yaml_text)

    assert data["Description"] == "Webservice for 'Service'. Restricted to user 'special'."
    assert data["FrameworkVersion"] == "12.0.0"

    route_mapping = data["Provider"]["Transport"]["Config"]["RouteOperationMapping"]
    assert route_mapping == {
        "Ticket::TicketCreate": {
            "Route": "/ticket-create",
            "RequestMethod": ["POST"],
            "ParserBackend": "JSON",
        },
        "Ticket::TicketSearch": {
            "Route": "/ticket-search",
            "RequestMethod": ["POST"],
            "ParserBackend": "JSON",
        },
    }

    operations = data["Provider"]["Operation"]
    assert set(operations) == {"TicketCreate", "TicketSearch"}
    create_op = operations["TicketCreate"]
    assert create_op["Type"] == TicketOperation.CREATE.type
    assert create_op["IncludeTicketData"] == "1"
    assert create_op["MappingInbound"]["Config"]["ValueMap"]["UserLogin"]["ValueMapRegEx"] == {".*": "special"}
    outbound_expected = generator._create_simple_empty_mapping()
    assert create_op["MappingOutbound"] == outbound_expected

    search_op = operations["TicketSearch"]
    assert search_op["Type"] == TicketOperation.SEARCH.type
    assert search_op["IncludeTicketData"] == "0"
    assert search_op["MappingOutbound"] == outbound_expected


def test_generate_yaml_requires_operations() -> None:
    generator = sw.WebServiceGenerator()
    with pytest.raises(ValueError, match="No operations enabled"):
        generator.generate_yaml("Service", [], None)


def test_write_yaml_to_file_uses_result(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_generate(self, webservice_name, enabled_operations, restricted_user, framework_version):
        captured["args"] = {
            "webservice_name": webservice_name,
            "enabled_operations": enabled_operations,
            "restricted_user": restricted_user,
            "framework_version": framework_version,
        }
        return "generated"

    monkeypatch.setattr(sw.WebServiceGenerator, "generate_yaml", fake_generate)

    generator = sw.WebServiceGenerator()
    output = tmp_path / "ws.yml"
    generator.write_yaml_to_file(
        webservice_name="Service",
        enabled_operations=[TicketOperation.UPDATE],
        restricted_user="agent",
        framework_version="10.0.0",
        file_path=output,
    )

    assert output.read_text(encoding="utf-8") == "generated"
    assert captured["args"] == {
        "webservice_name": "Service",
        "enabled_operations": [TicketOperation.UPDATE],
        "restricted_user": "agent",
        "framework_version": "10.0.0",
    }


def test_cli_requires_authentication_choice() -> None:
    result = runner.invoke(
        sw.app,
        ["--name", "Service", "--op", "get"],
    )
    assert result.exit_code == 1
    assert "must specify an authentication mode" in result.output


def test_cli_rejects_conflicting_authentication_options() -> None:
    result = runner.invoke(
        sw.app,
        [
            "--name",
            "Service",
            "--op",
            "get",
            "--allow-user",
            "agent",
            "--allow-all-agents",
        ],
    )
    assert result.exit_code == 1
    assert "mutually exclusive" in result.output


def test_cli_outputs_generated_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class DummyGenerator:
        def generate_yaml(self, **kwargs):
            captured["kwargs"] = kwargs
            return "---\nkey: value\n"

    monkeypatch.setattr(sw, "WebServiceGenerator", lambda: DummyGenerator())

    result = runner.invoke(
        sw.app,
        [
            "--name",
            "Service",
            "--op",
            "create",
            "--allow-all-agents",
        ],
    )

    assert result.exit_code == 0
    assert "--- Generated YAML ---" in result.output
    assert "key: value" in result.output
    assert captured["kwargs"]["webservice_name"] == "Service"
    assert captured["kwargs"]["enabled_operations"] == [TicketOperation.CREATE]
    assert captured["kwargs"]["restricted_user"] is None


def test_cli_writes_generated_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class DummyGenerator:
        def write_yaml_to_file(self, **kwargs):
            captured["kwargs"] = kwargs

    monkeypatch.setattr(sw, "WebServiceGenerator", lambda: DummyGenerator())

    file_path = tmp_path / "config.yml"
    result = runner.invoke(
        sw.app,
        [
            "--name",
            "Service",
            "--op",
            "update",
            "--allow-user",
            "agent",
            "--file",
            str(file_path),
        ],
    )

    assert result.exit_code == 0
    assert "Successfully generated webservice configuration." in result.output
    assert f"File: {file_path}" in result.output
    assert captured["kwargs"]["webservice_name"] == "Service"
    assert captured["kwargs"]["enabled_operations"] == [TicketOperation.UPDATE]
    assert captured["kwargs"]["restricted_user"] == "agent"
    assert captured["kwargs"]["framework_version"] == "11.0.0"
    assert captured["kwargs"]["file_path"] == str(file_path)
