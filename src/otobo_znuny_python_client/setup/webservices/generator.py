from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Iterable

import typer
import yaml

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.utils import generate_enabled_operations_list
from setup.webservices import SUPPORTED_OPERATION_SPECS, SUPPORTED_OPERATIONS_DOC
from setup.webservices.webservice_models import NoAliasDumper, RouteMappingConfig, ProviderOperationConfig, \
    OperationSpec

DEFAULT_FRAMEWORK_VERSION = "11.0.0"
DEFAULT_BASIC_AUTH_USER = "webservice"


class WebServiceGenerator:
    """Build YAML snippets for OTOBO/Znuny ticket web services."""

    def __init__(self) -> None:
        self.name = ""
        self.description = ""
        self.framework_version = DEFAULT_FRAMEWORK_VERSION
        self.basic_auth_user = DEFAULT_BASIC_AUTH_USER
        self.basic_auth_password = ""
        self.operation_specs = operation_specs or SUPPORTED_OPERATION_SPECS

    @staticmethod
    def build_description(
            name: str,
            restricted_user: str | None = None,
            allow_all_agents: bool = True,
    ) -> str:
        if restricted_user:
            return (
                f"Webservice '{name}' secured for the dedicated agent '{restricted_user}'."
            )
        if allow_all_agents:
            return (
                f"Webservice '{name}' for Python client integrations. Accessible to"
                " authenticated agents with the required permissions."
            )
        return f"Webservice '{name}' for Python client integrations."

    def build_config(self, operations: Iterable[TicketOperation]) -> dict[str, Any]:
        """Generate a complete web service configuration for the selected operations."""
        config: dict[str, dict[str, dict[str, dict[str, Any] | str] | str] | str] = {
            "Debugger": {
                "DebugThreshold": "debug",
                "TestMode": "0",
            },
            "Description": self.description,
            "FrameworkVersion": self.framework_version,
            "Provider": {
                "Operation": {},
                "Transport": {
                    "Config": {
                        "AdditionalHeaders": "",
                        "InboundLogging": "1",
                        "MaxLength": "100000000",
                        "OutboundLogging": "1",
                        "RouteOperationMapping": {},
                    },
                    "Type": "HTTP::REST",
                },
            },
            "RemoteSystem": "",
            "Requester": {
                "Transport": {
                    "Type": "",
                },
            },
        }

        route_mapping: dict = config["Provider"]["Transport"]["Config"]["RouteOperationMapping"]
        operations_map: dict = config["Provider"]["Operation"]

        for operation in operations:
            spec = self.operation_specs.get(operation)
            if spec is None:
                continue

            operations_map[spec.op.value] = self._create_operation_config(spec)
            route_mapping[spec.route] = RouteMappingConfig(
                Route=spec.route,
                RequestMethod=spec.methods,
            ).model_dump()

        return config

    def _create_operation_config(self, op_spec: OperationSpec) -> dict[str, Any]:
        return ProviderOperationConfig(
            Type=f"Ticket::{op_spec.op.value}",
            Description=op_spec.description,
            IncludeTicketData=op_spec.include_ticket_data,
            MappingInbound={
                "Type": "Simple",
                "Config": {
                    "Template": op_spec.inbound_template,
                },
            },
            MappingOutbound={
                "Type": "Simple",
                "Config": {},
            },
        ).model_dump()

    def dump_yaml(self, config: dict[str, Any]) -> str:
        """Serialize a web service configuration into YAML."""

        return yaml.dump(config, Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False, indent=2)

    def save_to_file(self, config: dict[str, Any], output_path: Path) -> None:
        """Persist a YAML configuration to disk."""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.dump_yaml(config), encoding="utf-8")


CLI_DESCRIPTION = "\n\n".join([
    "Generate secure OTOBO/Znuny web service YAML.",
    SUPPORTED_OPERATIONS_DOC,
    AUTH_EXPECTATIONS_DOC,
])

app = typer.Typer(
    add_completion=False,
    help=CLI_DESCRIPTION,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command(help="\n\n".join([SUPPORTED_OPERATIONS_DOC, AUTH_EXPECTATIONS_DOC]))
def generate(
        name: Annotated[
            str,
            typer.Option(help="Name of the web service"),
        ] = "PythonClientWebService",
        description: Annotated[
            str,
            typer.Option(help="Description of the web service"),
        ] = "Web service for Python client integration",
        framework_version: Annotated[
            str,
            typer.Option(help="Framework version for the generated YAML"),
        ] = DEFAULT_FRAMEWORK_VERSION,
        operations: Annotated[
            list[str] | None,
            typer.Option(
                help="Enabled operations (repeat for multiple)",
                show_default="all",
            ),
        ] = None,
        restricted
        output: Annotated[
            Path,
            typer.Option(help="Output file path"),
        ] = Path("webservice_config.yml"),
) -> None:
    """Generate OTOBO/Znuny web service configuration."""

    selected_operations = operations or [op.name.lower() for op in SUPPORTED_OPERATION_SPECS]
    enabled_ops = generate_enabled_operations_list(selected_operations)
    if not enabled_ops:
        typer.echo("Error: No valid operations specified", err=True)
        raise typer.Exit(1)

    generator = WebServiceGenerator(
        name=name,
        description=description,
        framework_version=framework_version,
        basic_auth_user=basic_auth_user,
    )
    config = generator.build_config(enabled_ops)
    generator.save_to_file(config, output)

    typer.echo(f"Web service configuration generated: {output}")
    typer.echo(f"Operations included: {[op.value for op in enabled_ops]}")


if __name__ == "__main__":
    app()
