import yaml
import typer
import re
import copy
from pathlib import Path
from typing import Any, Annotated


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


app = typer.Typer(
    add_completion=False,
    help="A CLI tool to generate secure OTOBO/Znuny web service YAML configurations.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


class WebServiceGenerator:
    DEFAULT_OPERATIONS: dict[str, dict[str, Any]] = {
        "TicketCreate": {
            "name": "ticket-create",
            "type": "Ticket::TicketCreate",
            "description": "Creates a new ticket.",
            "methods": ["POST"],
            "include_ticket_data": "1",
        },
        "TicketGet": {
            "name": "ticket-get",
            "type": "Ticket::TicketGet",
            "description": "Retrieves ticket information by ID.",
            "methods": ["POST"],
            "include_ticket_data": "0",
        },
        "TicketSearch": {
            "name": "ticket-search",
            "type": "Ticket::TicketSearch",
            "description": "Searches for tickets based on specified criteria.",
            "methods": ["POST"],
            "include_ticket_data": "0",
        },
        "TicketUpdate": {
            "name": "ticket-update",
            "type": "Ticket::TicketUpdate",
            "description": "Updates an existing ticket.",
            "methods": ["PUT"],
            "include_ticket_data": "1",
        },
    }

    def _create_inbound_mapping(self, restricted_user: str | None) -> dict[str, Any]:
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

    def generate_yaml(
            self,
            webservice_name: str,
            enabled_operations: dict[str, dict[str, str] | None],
            restricted_user: str | None = None,
            framework_version: str = "11.0.0",
    ) -> str:
        if not webservice_name:
            raise ValueError("Webservice name cannot be empty.")
        if not re.fullmatch(r"[A-Za-z]+", webservice_name):
            raise ValueError(
                "Webservice name must only contain upper/lowercase letters (A–Z, a–z), no spaces or symbols.")

        operations_config: dict[str, Any] = {}
        route_mapping_config: dict[str, Any] = {}
        inbound_mapping_base = self._create_inbound_mapping(restricted_user)
        description = (
            f"Webservice for '{webservice_name}'. Restricted to user '{restricted_user}'."
            if restricted_user
            else f"Webservice for '{webservice_name}'. Accessible by all permitted agents."
        )

        for key in enabled_operations:
            defaults = self.DEFAULT_OPERATIONS.get(key)
            if not defaults:
                continue
            inbound_mapping = copy.deepcopy(inbound_mapping_base)
            op_key, route = defaults["name"], f"/{defaults['name']}"
            operations_config[op_key] = {
                "Type": defaults["type"],
                "Description": defaults["description"],
                "IncludeTicketData": defaults["include_ticket_data"],
                "MappingInbound": inbound_mapping,
                "MappingOutbound": {
                    "Type": "Simple",
                    "Config": {
                        "KeyMapDefault": {"MapTo": "", "MapType": "Keep"},
                        "ValueMapDefault": {"MapTo": "", "MapType": "Keep"},
                    },
                },
            }
            route_mapping_config[op_key] = {
                "Route": route,
                "RequestMethod": defaults["methods"],
                "ParserBackend": "JSON",
            }

        final_yaml_structure: dict[str, Any] = {
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
                        "RouteOperationMapping": route_mapping_config,
                    },
                },
                "Operation": operations_config,
            },
            "RemoteSystem": "",
            "Requester": {"Transport": {"Type": ""}},
        }

        return yaml.dump(final_yaml_structure, sort_keys=False, indent=2, Dumper=NoAliasDumper, explicit_start=True)


@app.command()
def generate(
        name: Annotated[
            str,
            typer.Option("--name", help="Display name for the web service (only A–Z letters, no spaces).",
                         rich_help_panel="Required Settings"),
        ],
        enable_ticket_get: Annotated[
            bool, typer.Option("--enable-ticket-get", help="Enable TicketGet operation.", rich_help_panel="Operations")
        ] = False,
        enable_ticket_search: Annotated[
            bool, typer.Option("--enable-ticket-search", help="Enable TicketSearch operation.",
                               rich_help_panel="Operations")
        ] = False,
        enable_ticket_create: Annotated[
            bool, typer.Option("--enable-ticket-create", help="Enable TicketCreate operation.",
                               rich_help_panel="Operations")
        ] = False,
        enable_ticket_update: Annotated[
            bool, typer.Option("--enable-ticket-update", help="Enable TicketUpdate operation.",
                               rich_help_panel="Operations")
        ] = False,
        allow_user: Annotated[
            str | None,
            typer.Option("--allow-user", metavar="USERNAME", help="Secure Mode: Restrict usage to a single agent.",
                         rich_help_panel="Authentication Mode (Choose one)"),
        ] = None,
        allow_all_agents: Annotated[
            bool,
            typer.Option("--allow-all-agents", help="Open Mode: Allow any agent to use the web service.",
                         rich_help_panel="Authentication Mode (Choose one)"),
        ] = False,
        version: Annotated[
            str,
            typer.Option("--version", help="FrameworkVersion (e.g., '11.0.0' for OTOBO, '7.1.7' for Znuny).",
                         rich_help_panel="Optional Settings"),
        ] = "11.0.0",
        file: Annotated[
            str | None,
            typer.Option("--file", metavar="FILENAME", help="Output file name. If not provided, prints to console.",
                         rich_help_panel="Optional Settings"),
        ] = None,
):
    if not (allow_user or allow_all_agents):
        typer.secho("Error: You must specify an authentication mode.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if allow_user and allow_all_agents:
        typer.secho("Error: --allow-user and --allow-all-agents are mutually exclusive.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    enabled = []
    if enable_ticket_get:
        enabled.append("TicketGet")
    if enable_ticket_search:
        enabled.append("TicketSearch")
    if enable_ticket_create:
        enabled.append("TicketCreate")
    if enable_ticket_update:
        enabled.append("TicketUpdate")
    if not enabled:
        typer.secho("Error: You must enable at least one operation.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    generator = WebServiceGenerator()
    operations_to_enable = {op: None for op in enabled}
    restricted_user = allow_user if allow_user else None

    try:
        webservice_yaml_output = generator.generate_yaml(
            webservice_name=name,
            restricted_user=restricted_user,
            enabled_operations=operations_to_enable,
            framework_version=version,
        )
        if file:
            Path(file).write_text(webservice_yaml_output, encoding="utf-8")
            typer.secho("Successfully generated webservice configuration!", fg=typer.colors.GREEN)
            typer.secho(f"File saved as: {file}")
        else:
            typer.secho("--- Generated YAML Content ---", bold=True)
            print(webservice_yaml_output)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
