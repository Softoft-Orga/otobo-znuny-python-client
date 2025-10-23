from __future__ import annotations

import copy
from pathlib import Path
import re
from typing import Annotated, Any, Literal

from pydantic import BaseModel
import typer
import yaml

from otobo_znuny.domain_models.ticket_operation import TicketOperation
from .utils import generate_enabled_operations_list


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


app = typer.Typer(
    add_completion=False,
    help="Generate secure OTOBO/Znuny web service YAML.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


class RouteMappingConfig(BaseModel):
    Route: str
    RequestMethod: list[str]
    ParserBackend: Literal["JSON"] = "JSON"


class ProviderOperationConfig(BaseModel):
    Type: str
    Description: str
    IncludeTicketData: Literal["0", "1"]
    MappingInbound: dict[str, Any]
    MappingOutbound: dict[str, Any]


class OperationSpec(BaseModel):
    op: TicketOperation
    route: str
    description: str
    methods: list[str]
    include_ticket_data: Literal["0", "1"]


class WebServiceGenerator:
    def __init__(self, name: str, description: str, password: str):
        self.name = name
        self.description = description
        self.password = password

    def generate_webservice_config(self, operations: list[OperationSpec]) -> dict[str, Any]:
        """Generate a complete web service configuration."""
        config = {
            "Debugger": {
                "DebugThreshold": "debug",
                "TestMode": "0"
            },
            "Description": self.description,
            "FrameworkVersion": "10.1.x git",
            "Provider": {
                "Operation": {},
                "Transport": {
                    "Config": {
                        "AdditionalHeaders": None,
                        "Authentication": {
                            "AuthType": "BasicAuth",
                            "BasicAuthPassword": self.password,
                            "BasicAuthUser": "webservice"
                        },
                        "InboundLogging": "1",
                        "MaxLength": "100000000",
                        "OutboundLogging": "1",
                        "RouteOperationMapping": {}
                    },
                    "Type": "HTTP::REST"
                }
            },
            "RemoteSystem": "",
            "Requester": {
                "Transport": {
                    "Type": ""
                }
            }
        }

        # Add operations
        for op_spec in operations:
            operation_config = self._create_operation_config(op_spec)
            config["Provider"]["Operation"][op_spec.op.value] = operation_config
            
            # Add route mapping
            route_config = RouteMappingConfig(
                Route=op_spec.route,
                RequestMethod=op_spec.methods
            )
            config["Provider"]["Transport"]["Config"]["RouteOperationMapping"][op_spec.route] = route_config.model_dump()

        return config

    def _create_operation_config(self, op_spec: OperationSpec) -> dict[str, Any]:
        """Create operation configuration for a specific operation."""
        base_config = {
            "Type": f"Ticket::{op_spec.op.value}",
            "Description": op_spec.description,
            "IncludeTicketData": op_spec.include_ticket_data,
            "MappingInbound": {},
            "MappingOutbound": {}
        }

        # Add operation-specific mappings
        if op_spec.op == TicketOperation.CREATE:
            base_config["MappingInbound"] = {
                "Config": {
                    "Template": "{\n  \"Ticket\": {\n    \"Title\": \"<OTOBO_Ticket_Title>\",\n    \"Queue\": \"<OTOBO_Ticket_Queue>\",\n    \"State\": \"<OTOBO_Ticket_State>\",\n    \"Priority\": \"<OTOBO_Ticket_Priority>\",\n    \"CustomerUser\": \"<OTOBO_Ticket_CustomerUser>\"\n  },\n  \"Article\": {\n    \"Subject\": \"<OTOBO_Article_Subject>\",\n    \"Body\": \"<OTOBO_Article_Body>\",\n    \"ContentType\": \"text/plain; charset=utf8\",\n    \"CommunicationChannel\": \"Internal\",\n    \"SenderType\": \"agent\"\n  }\n}"
                },
                "Type": "Simple"
            }
        elif op_spec.op == TicketOperation.GET:
            base_config["MappingInbound"] = {
                "Config": {
                    "Template": "{\n  \"TicketID\": \"<OTOBO_TicketID>\"\n}"
                },
                "Type": "Simple"
            }
        elif op_spec.op == TicketOperation.SEARCH:
            base_config["MappingInbound"] = {
                "Config": {
                    "Template": "{\n  \"Title\": \"<OTOBO_Title>\",\n  \"Queue\": \"<OTOBO_Queue>\",\n  \"State\": \"<OTOBO_State>\",\n  \"Priority\": \"<OTOBO_Priority>\",\n  \"CustomerUserLogin\": \"<OTOBO_CustomerUserLogin>\"\n}"
                },
                "Type": "Simple"
            }
        elif op_spec.op == TicketOperation.UPDATE:
            base_config["MappingInbound"] = {
                "Config": {
                    "Template": "{\n  \"TicketID\": \"<OTOBO_TicketID>\",\n  \"Ticket\": {\n    \"Title\": \"<OTOBO_Ticket_Title>\",\n    \"Queue\": \"<OTOBO_Ticket_Queue>\",\n    \"State\": \"<OTOBO_Ticket_State>\",\n    \"Priority\": \"<OTOBO_Ticket_Priority>\"\n  }\n}"
                },
                "Type": "Simple"
            }

        return base_config

    def save_to_file(self, config: dict[str, Any], output_path: Path) -> None:
        """Save the web service configuration to a YAML file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, Dumper=NoAliasDumper, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, indent=2)


@app.command()
def generate(
    name: Annotated[str, typer.Option(help="Name of the web service")] = "PythonClientWebService",
    description: Annotated[str, typer.Option(help="Description of the web service")] = "Web service for Python client integration",
    password: Annotated[str, typer.Option(help="Password for BasicAuth authentication")] = "secure_password_123",
    operations: Annotated[list[str], typer.Option(help="Enabled operations (get, search, create, update)")] = ["get", "search", "create", "update"],
    output: Annotated[Path, typer.Option(help="Output file path")] = Path("webservice_config.yml"),
) -> None:
    """Generate OTOBO/Znuny web service configuration."""
    
    # Validate and convert operations
    enabled_ops = generate_enabled_operations_list(operations)
    if not enabled_ops:
        typer.echo("Error: No valid operations specified", err=True)
        raise typer.Exit(1)

    # Create operation specifications
    operation_specs = []
    for op in enabled_ops:
        if op == TicketOperation.GET:
            spec = OperationSpec(
                op=op,
                route="/tickets/:TicketID",
                description="Get ticket by ID",
                methods=["GET"],
                include_ticket_data="1"
            )
        elif op == TicketOperation.SEARCH:
            spec = OperationSpec(
                op=op,
                route="/tickets/search",
                description="Search for tickets",
                methods=["POST"],
                include_ticket_data="1"
            )
        elif op == TicketOperation.CREATE:
            spec = OperationSpec(
                op=op,
                route="/tickets",
                description="Create a new ticket",
                methods=["POST"],
                include_ticket_data="1"
            )
        elif op == TicketOperation.UPDATE:
            spec = OperationSpec(
                op=op,
                route="/tickets/:TicketID",
                description="Update an existing ticket",
                methods=["PUT", "PATCH"],
                include_ticket_data="1"
            )
        else:
            continue
            
        operation_specs.append(spec)

    # Generate configuration
    generator = WebServiceGenerator(name, description, password)
    config = generator.generate_webservice_config(operation_specs)
    
    # Save to file
    generator.save_to_file(config, output)
    
    typer.echo(f"Web service configuration generated: {output}")
    typer.echo(f"Operations included: {[op.value for op in enabled_ops]}")


if __name__ == "__main__":
    app()
