from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any, Annotated, Dict, List, Literal

import typer
import yaml
from pydantic import BaseModel

from otobo import TicketOperation


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
            route="ticket/search",
            description="Searches for tickets based on criteria.",
            methods=["POST"],
            include_ticket_data="0",
        ),
        TicketOperation.UPDATE: OperationSpec(
            op=TicketOperation.UPDATE,
            route="ticket/update",
            description="Updates an existing ticket.",
            methods=["PUT"],
            include_ticket_data="1",
        ),
    }

    def _create_operation_configs(self, s: OperationSpec, inbound: Dict[str, Any]) -> dict[str, dict]:
        return ProviderOperationConfig(
            Type=s.op.type,
            Description=s.description,
            IncludeTicketData=s.include_ticket_data,
            MappingInbound=inbound,
            MappingOutbound=self._outbound_mapping(),
        ).model_dump()

    def generate_yaml(
            self,
            webservice_name: str,
            enabled_operations: List[TicketOperation],
            restricted_user: str | None = None,
            framework_version: str = "11.0.0",
    ) -> str:
        name = self._validate_name(webservice_name)
        specs = [self.DEFAULT_SPECS[o] for o in enabled_operations if o in self.DEFAULT_SPECS]
        if not specs:
            raise ValueError("No operations enabled.")
        inbound_base = self._inbound_mapping(restricted_user)
        description = self._description(name, restricted_user)
        route_mapping: dict[str, dict] = {}
        operations: dict[str, dict] = {}
        for s in specs:
            inbound = copy.deepcopy(inbound_base)
            route_mapping[s.provider_name] = RouteMappingConfig(
                Route=f"/{s.route}",
                RequestMethod=s.methods,
            ).model_dump()
            operations[s.provider_name] = self._create_operation_configs(s, inbound)
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
                        "RouteOperationMapping": route_mapping,
                    },
                },
                "Operation": operations,
            },
            "RemoteSystem": "",
            "Requester": {"Transport": {"Type": ""}},
        }
        return yaml.dump(data, sort_keys=False, indent=2, Dumper=NoAliasDumper, explicit_start=True)

    def _validate_name(self, name: str) -> str:
        if not name:
            raise ValueError("Webservice name cannot be empty.")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
            raise ValueError("Name must start with a letter and contain only A–Z, a–z, 0–9, _ or -.")
        return name

    def _description(self, name: str, user: str | None) -> str:
        if user:
            return f"Webservice for '{name}'. Restricted to user '{user}'."
        return f"Webservice for '{name}'. Accessible by all permitted agents."

    def _inbound_mapping(self, restricted_user: str | None) -> Dict[str, Any]:
        if restricted_user:
            return {
                "Type": "Simple",
                "Config": {
                    "KeyMapDefault": {"MapType": "Keep", "MapTo": ""},
                    "KeyMapExact": {"UserLogin": "UserLogin"},
                    "ValueMap": {"UserLogin": {"ValueMapRegEx": {".*": restricted_user}}},
                    "ValueMapDefault": {"MapType": "Keep", "MapTo": ""},
                },
            }
        return {
            "Type": "Simple",
            "Config": {
                "KeyMapDefault": {"MapType": "Keep", "MapTo": ""},
                "ValueMapDefault": {"MapType": "Keep", "MapTo": ""},
            },
        }

    def _outbound_mapping(self) -> Dict[str, Any]:
        return {
            "Type": "Simple",
            "Config": {
                "KeyMapDefault": {"MapTo": "", "MapType": "Keep"},
                "ValueMapDefault": {"MapTo": "", "MapType": "Keep"},
            },
        }


@app.command()
def generate(
        name: Annotated[str, typer.Option("--name", rich_help_panel="Required")],
        enable_ticket_get: Annotated[bool, typer.Option("--enable-ticket-get", rich_help_panel="Operations")] = False,
        enable_ticket_search: Annotated[
            bool, typer.Option("--enable-ticket-search", rich_help_panel="Operations")] = False,
        enable_ticket_create: Annotated[
            bool, typer.Option("--enable-ticket-create", rich_help_panel="Operations")] = False,
        enable_ticket_update: Annotated[
            bool, typer.Option("--enable-ticket-update", rich_help_panel="Operations")] = False,
        allow_user: Annotated[
            str | None, typer.Option("--allow-user", metavar="USERNAME", rich_help_panel="Auth")] = None,
        allow_all_agents: Annotated[bool, typer.Option("--allow-all-agents", rich_help_panel="Auth")] = False,
        version: Annotated[str, typer.Option("--version", rich_help_panel="Optional")] = "11.0.0",
        file: Annotated[str | None, typer.Option("--file", metavar="FILENAME", rich_help_panel="Optional")] = None,
):
    if not (allow_user or allow_all_agents):
        typer.secho("Error: You must specify an authentication mode.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if allow_user and allow_all_agents:
        typer.secho("Error: --allow-user and --allow-all-agents are mutually exclusive.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    enabled: list[TicketOperation] = [
        op
        for op, ok in [
            (TicketOperation.GET, enable_ticket_get),
            (TicketOperation.SEARCH, enable_ticket_search),
            (TicketOperation.CREATE, enable_ticket_create),
            (TicketOperation.UPDATE, enable_ticket_update),
        ]
        if ok
    ]
    gen = WebServiceGenerator()
    try:
        out = gen.generate_yaml(
            webservice_name=name,
            enabled_operations=enabled,
            restricted_user=allow_user if allow_user else None,
            framework_version=version,
        )
        if file:
            Path(file).write_text(out, encoding="utf-8")
            typer.secho("Successfully generated webservice configuration.", fg=typer.colors.GREEN)
            typer.secho(f"File: {file}")
        else:
            typer.secho("--- Generated YAML ---", bold=True)
            print(out)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
