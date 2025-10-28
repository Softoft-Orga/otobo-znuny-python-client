from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Iterable, Literal

import typer
import yaml
from pydantic import BaseModel

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.utils import generate_enabled_operations_list


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


DEFAULT_FRAMEWORK_VERSION = "11.0.0"
DEFAULT_BASIC_AUTH_USER = "webservice"
DEFAULT_BASIC_AUTH_PASSWORD = "secure_password_123"


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
    inbound_template: str


SUPPORTED_OPERATION_SPECS: dict[TicketOperation, OperationSpec] = {
    TicketOperation.GET: OperationSpec(
        op=TicketOperation.GET,
        route="/tickets/:TicketID",
        description="Get ticket details by ID.",
        methods=["GET"],
        include_ticket_data="1",
        inbound_template='{\n  "TicketID": "<OTOBO_TicketID>"\n}',
    ),
    TicketOperation.SEARCH: OperationSpec(
        op=TicketOperation.SEARCH,
        route="/tickets/search",
        description="Search for tickets using the request payload as criteria.",
        methods=["POST"],
        include_ticket_data="1",
        inbound_template='{\n  "Title": "<OTOBO_Title>",\n  "Queue": "<OTOBO_Queue>",\n  "State": "<OTOBO_State>",\n  "Priority": "<OTOBO_Priority>",\n  "CustomerUserLogin": "<OTOBO_CustomerUserLogin>"\n}',
    ),
    TicketOperation.CREATE: OperationSpec(
        op=TicketOperation.CREATE,
        route="/tickets",
        description="Create a new ticket from the supplied Ticket and Article data.",
        methods=["POST"],
        include_ticket_data="1",
        inbound_template='{\n  "Ticket": {\n    "Title": "<OTOBO_Ticket_Title>",\n    "Queue": "<OTOBO_Ticket_Queue>",\n    "State": "<OTOBO_Ticket_State>",\n    "Priority": "<OTOBO_Ticket_Priority>",\n    "CustomerUser": "<OTOBO_Ticket_CustomerUser>"\n  },\n  "Article": {\n    "Subject": "<OTOBO_Article_Subject>",\n    "Body": "<OTOBO_Article_Body>",\n    "ContentType": "text/plain; charset=utf8",\n    "CommunicationChannel": "Internal",\n    "SenderType": "agent"\n  }\n}',
    ),
    TicketOperation.UPDATE: OperationSpec(
        op=TicketOperation.UPDATE,
        route="/tickets/:TicketID",
        description="Update an existing ticket identified by the path parameter.",
        methods=["PUT", "PATCH"],
        include_ticket_data="1",
        inbound_template='{\n  "TicketID": "<OTOBO_TicketID>",\n  "Ticket": {\n    "Title": "<OTOBO_Ticket_Title>",\n    "Queue": "<OTOBO_Ticket_Queue>",\n    "State": "<OTOBO_Ticket_State>",\n    "Priority": "<OTOBO_Ticket_Priority>"\n  }\n}',
    ),
}


def _build_operations_doc(specs: Iterable[OperationSpec]) -> str:
    lines = ["Supported operations and routes:"]
    for spec in specs:
        methods = ", ".join(spec.methods)
        lines.append(
            f"- {spec.op.name.lower()}: {spec.description}"
            f" (Route: {spec.route}, Methods: {methods})"
        )
    return "\n".join(lines)


SUPPORTED_OPERATIONS_DOC = _build_operations_doc(SUPPORTED_OPERATION_SPECS.values())

AUTH_EXPECTATIONS_DOC = (
    "Authentication: HTTP Basic authentication is configured for the provider transport.\n"
    f"The generated YAML defaults to user '{DEFAULT_BASIC_AUTH_USER}'. Provide the desired"
    " password when calling the generator to align with your deployment policies."
)


class WebServiceGenerator:
    """Build YAML snippets for OTOBO/Znuny ticket web services."""

    def __init__(
            self,
            name: str,
            description: str,
            *,
            framework_version: str = DEFAULT_FRAMEWORK_VERSION,
            basic_auth_user: str = DEFAULT_BASIC_AUTH_USER,
            basic_auth_password: str | None = DEFAULT_BASIC_AUTH_PASSWORD,
            operation_specs: dict[TicketOperation, OperationSpec] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.framework_version = framework_version
        self.basic_auth_user = basic_auth_user
        self.basic_auth_password = basic_auth_password or ""
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

        config = {
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
                        "AdditionalHeaders": None,
                        "Authentication": {
                            "AuthType": "BasicAuth",
                            "BasicAuthPassword": self.basic_auth_password,
                            "BasicAuthUser": self.basic_auth_user,
                        },
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

        route_mapping = config["Provider"]["Transport"]["Config"]["RouteOperationMapping"]
        operations_map = config["Provider"]["Operation"]

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

        return yaml.dump(
            config,
            Dumper=NoAliasDumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
        )

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
        password: Annotated[
            str,
            typer.Option(help="Password for BasicAuth authentication"),
        ] = DEFAULT_BASIC_AUTH_PASSWORD,
        basic_auth_user: Annotated[
            str,
            typer.Option(help="Username for BasicAuth authentication"),
        ] = DEFAULT_BASIC_AUTH_USER,
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
        basic_auth_password=password,
    )
    config = generator.build_config(enabled_ops)
    generator.save_to_file(config, output)

    typer.echo(f"Web service configuration generated: {output}")
    typer.echo(f"Operations included: {[op.value for op in enabled_ops]}")


if __name__ == "__main__":
    app()
