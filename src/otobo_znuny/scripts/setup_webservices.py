from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any, Annotated, Dict, List, Literal, Optional, Union

import typer
import yaml
from pydantic import BaseModel

from otobo_znuny.domain_models.ticket_operation import TicketOperation
from otobo_znuny.scripts.webservice_util import generate_enabled_operations_list


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
    RequestMethod: List[str]
    ParserBackend: Literal["JSON"] = "JSON"


class ProviderOperationConfig(BaseModel):
    Type: str
    Description: str
    IncludeTicketData: Literal["0", "1"]
    MappingInbound: Dict[str, Any]
    MappingOutbound: Dict[str, Any]


class OperationSpec(BaseModel):
    op: TicketOperation
    route: str
    description: str
    methods: List[str]
    include_ticket_data: Literal["0", "1"]


class WebServiceGenerator:
    DEFAULT_SPECS: dict[TicketOperation, OperationSpec] = {
        TicketOperation.CREATE: OperationSpec(
            op=TicketOperation.CREATE,
            route="ticket-create",
            description="Creates a new ticket.",
            methods=["POST"],
            include_ticket_data="1",
        ),
        TicketOperation.GET: OperationSpec(
            op=TicketOperation.GET,
            route="ticket-get",
            description="Retrieves a ticket by its ID.",
            methods=["POST"],
            include_ticket_data="1",
        ),
        TicketOperation.SEARCH: OperationSpec(
            op=TicketOperation.SEARCH,
            route="ticket-search",
            description="Searches for tickets based on criteria.",
            methods=["POST"],
            include_ticket_data="0",
        ),
        TicketOperation.UPDATE: OperationSpec(
            op=TicketOperation.UPDATE,
            route="ticket-update",
            description="Updates an existing ticket.",
            methods=["PUT"],
            include_ticket_data="1",
        ),
    }

    def __init__(self):
        self.route_mapping: dict[str, dict] = {}
        self.operations: dict[str, dict] = {}

    def generate_yaml(
            self,
            webservice_name: str,
            enabled_operations: List[TicketOperation],
            restricted_user: Optional[str] = None,
            framework_version: str = "11.0.0",
    ) -> str:
        name = self._validate_name(webservice_name)
        enabled_operation_specs: list[OperationSpec] = [self.DEFAULT_SPECS[o] for o in enabled_operations if
                                                        o in self.DEFAULT_SPECS]
        if not enabled_operation_specs:
            raise ValueError("No operations enabled.")
        inbound_base = self._create_inbound_mapping(restricted_user)
        description = self._description(name, restricted_user)

        for s in enabled_operation_specs:
            inbound = copy.deepcopy(inbound_base)
            self._add_operation(s, inbound)

        data = {
            "Debugger": {"DebugThreshold": "debug", "TestMode": "0"},
            "Description": description,
            "FrameworkVersion": framework_version,
            "Provider": {
                "Transport": {
                    "Type": "HTTP::REST",
                    "Config": {
                        "MaxLength": "1000000",
                        "KeepAlive": "",
                        "AdditionalHeaders": "",
                        "RouteOperationMapping": self.route_mapping,
                    },
                },
                "Operation": self.operations,
            },
            "RemoteSystem": "",
            "Requester": {"Transport": {"Type": ""}},
        }
        return yaml.dump(data, sort_keys=False, indent=2, Dumper=NoAliasDumper, explicit_start=True)

    def write_yaml_to_file(self, webservice_name: str,
                           enabled_operations: List[TicketOperation],
                           restricted_user: Optional[str] = None,
                           framework_version: str = "11.0.0",
                           file_path: Union[str, Path] = "webservice_config.yml") -> None:
        out = self.generate_yaml(
            webservice_name=webservice_name,
            enabled_operations=enabled_operations,
            restricted_user=restricted_user,
            framework_version=framework_version,
        )
        Path(file_path).write_text(out, encoding="utf-8")

    def _add_operation(self, s: OperationSpec, inbound: Dict[str, Any]) -> None:
        self.route_mapping[s.op.operation_type] = RouteMappingConfig(
            Route=f"/{s.route}",
            RequestMethod=s.methods,
        ).model_dump()
        self.operations[s.provider_name] = ProviderOperationConfig(
            Type=s.op.type,
            Description=s.description,
            IncludeTicketData=s.include_ticket_data,
            MappingInbound=inbound,
            MappingOutbound=self._outbound_mapping(),
        ).model_dump()

    def _validate_name(self, name: str) -> str:
        if not name:
            raise ValueError("Webservice name cannot be empty.")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
            raise ValueError("Name must start with a letter and contain only A–Z, a–z, 0–9, _ or -.")
        return name

    def _description(self, name: str, user: Optional[str]) -> str:
        if user:
            return f"Webservice for '{name}'. Restricted to user '{user}'."
        return f"Webservice for '{name}'. Accessible by all permitted agents."

    def _create_simple_empty_mapping(self) -> Dict[str, Any]:
        return {"Type": "Simple", "Config": {"KeyMapDefault": self._create_empty_mapping(),
                                             "ValueMapDefault": self._create_empty_mapping()}}

    def _create_empty_mapping(self) -> Dict[str, Any]:
        return {"MapType": "Keep", "MapTo": ""}

    def _create_inbound_mapping(self, restricted_user: Optional[str]) -> Dict[str, Any]:
        if restricted_user:
            return {
                "Type": "Simple",
                "Config": {
                    "KeyMapDefault": self._create_empty_mapping(),
                    "KeyMapExact": {"UserLogin": "UserLogin"},
                    "ValueMap": {"UserLogin": {"ValueMapRegEx": {".*": restricted_user}}},
                    "ValueMapDefault": self._create_empty_mapping(),
                },
            }
        return self._create_simple_empty_mapping()

    def _outbound_mapping(self) -> Dict[str, Any]:
        return self._create_simple_empty_mapping()


@app.command()
def generate(
        name: Annotated[str, typer.Option("--name", rich_help_panel="Required")],
        enabled_operations_raw: List[str] = typer.Option(..., "--op", "-o",
                                                         help="Repeat for each: get, search, create, update",
                                                         case_sensitive=False),
        allow_user: Annotated[
            Optional[str], typer.Option("--allow-user", metavar="USERNAME", rich_help_panel="Auth")] = None,
        allow_all_agents: Annotated[bool, typer.Option("--allow-all-agents", rich_help_panel="Auth")] = False,
        version: Annotated[str, typer.Option("--version", rich_help_panel="Optional")] = "11.0.0",
        file: Annotated[Optional[str], typer.Option("--file", metavar="FILENAME", rich_help_panel="Optional")] = None,
):
    if not (allow_user or allow_all_agents):
        typer.secho("Error: You must specify an authentication mode.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if allow_user and allow_all_agents:
        typer.secho("Error: --allow-user and --allow-all-agents are mutually exclusive.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    enabled_operations: list[TicketOperation] = generate_enabled_operations_list(enabled_operations_raw)
    gen = WebServiceGenerator()
    try:

        if file:
            gen.write_yaml_to_file(
                webservice_name=name,
                enabled_operations=enabled_operations,
                restricted_user=allow_user if allow_user else None,
                framework_version=version,
                file_path=file,
            )
            typer.secho("Successfully generated webservice configuration.", fg=typer.colors.GREEN)
            typer.secho(f"File: {file}")
        else:
            out = gen.generate_yaml(
                webservice_name=name,
                enabled_operations=enabled_operations,
                restricted_user=allow_user if allow_user else None,
                framework_version=version,
            )
            typer.secho("--- Generated YAML ---", bold=True)
            typer.echo(out)

    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
