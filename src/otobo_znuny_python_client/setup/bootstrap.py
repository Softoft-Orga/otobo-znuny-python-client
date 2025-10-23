from __future__ import annotations

import secrets
import string
import subprocess
from pathlib import Path

import typer
from pydantic import BaseModel, ConfigDict

from otobo_znuny_python_client.cli.interface import OtoboCommandRunner, OtoboConsole
from otobo_znuny_python_client.domain_models.otobo_client_config import OperationUrlMap
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.generator import WebServiceGenerator

app = typer.Typer()

PermissionMap = {
    "owner": "owner",
    "move": "move_into",
    "priority": "priority",
    "create": "create",
    "read": "ro",
    "full": "rw",
}


def set_env_var(key: str, value: str, shell_rc: str = "~/.bashrc") -> None:
    rc_file = Path(shell_rc).expanduser()
    export_line = f'export {key}="{value}"\n'

    lines = rc_file.read_text().splitlines() if rc_file.exists() else []

    lines = [line for line in lines if not line.strip().startswith(f"export {key}=")]
    lines.append(export_line.strip())

    rc_file.write_text("\n".join(lines) + "\n")

    subprocess.run(f"export {key}='{value}'", shell=True, executable="/bin/bash")


class SystemEnvironment:
    def __init__(self, console_path: Path, webservices_dir: Path):
        self.console_path = console_path
        self.webservices_dir = webservices_dir

    def build_command_runner(self) -> OtoboCommandRunner:
        return OtoboCommandRunner.from_local(console_path=self.console_path)

    def __str__(self) -> str:
        return f"SystemEnvironment(console_path={self.console_path}, webservices_dir={self.webservices_dir})"


class DockerEnvironment:
    def __init__(self, container_name: str, console_path: str, webservices_dir: Path):
        self.container_name = container_name
        self.console_path = console_path
        self.webservices_dir = webservices_dir

    def build_command_runner(self) -> OtoboCommandRunner:
        return OtoboCommandRunner.from_docker(container=self.container_name, console_path=self.console_path)

    def __str__(self) -> str:
        return f"DockerEnvironment(container={self.container_name}, console_path={self.console_path}, webservices_dir={self.webservices_dir})"


class SetupConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    webservice_name: str
    webservice_password: str
    webservice_description: str
    enabled_operations: list[TicketOperation]

    group_name: str
    group_comment: str

    user_name: str
    user_first_name: str
    user_last_name: str
    user_email: str
    user_password: str
    user_permissions: list[str]

    queue_name: str
    queue_comment: str


def generate_random_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def setup_otobo_system(env: SystemEnvironment | DockerEnvironment, config: SetupConfig) -> None:
    """Set up OTOBO system with the provided configuration."""
    console = OtoboConsole(env.build_command_runner())

    typer.echo(f"Setting up OTOBO system using: {env}")

    # Create group
    typer.echo(f"Creating group: {config.group_name}")
    result = console.add_group(config.group_name, config.group_comment)
    if not result.ok:
        typer.echo(f"Failed to create group: {result.err}", err=True)
        return

    # Create user
    typer.echo(f"Creating user: {config.user_name}")
    result = console.add_user(
        config.user_name,
        config.user_first_name,
        config.user_last_name,
        config.user_email,
        config.user_password,
    )
    if not result.ok:
        typer.echo(f"Failed to create user: {result.err}", err=True)
        return

    # Link user to group with permissions
    for permission in config.user_permissions:
        mapped_permission = PermissionMap.get(permission, permission)
        typer.echo(f"Linking user {config.user_name} to group {config.group_name} with {mapped_permission} permission")
        result = console.link_user_to_group(config.user_name, config.group_name, mapped_permission)
        if not result.ok:
            typer.echo(f"Failed to link user to group: {result.err}", err=True)

    # Create queue
    typer.echo(f"Creating queue: {config.queue_name}")
    result = console.add_queue(config.queue_name, config.group_name, comment=config.queue_comment)
    if not result.ok:
        typer.echo(f"Failed to create queue: {result.err}", err=True)
        return

    # Generate and install web service
    typer.echo(f"Generating web service: {config.webservice_name}")
    generator = WebServiceGenerator(
        config.webservice_name,
        config.webservice_description,
        config.webservice_password,
    )

    # Create operation specs
    from .webservices.generator import OperationSpec
    operation_specs = []
    for op in config.enabled_operations:
        if op == TicketOperation.GET:
            spec = OperationSpec(
                op=op,
                route="/tickets/:TicketID",
                description="Get ticket by ID",
                methods=["GET"],
                include_ticket_data="1",
            )
        elif op == TicketOperation.SEARCH:
            spec = OperationSpec(
                op=op,
                route="/tickets/search",
                description="Search for tickets",
                methods=["POST"],
                include_ticket_data="1",
            )
        elif op == TicketOperation.CREATE:
            spec = OperationSpec(
                op=op,
                route="/tickets",
                description="Create a new ticket",
                methods=["POST"],
                include_ticket_data="1",
            )
        elif op == TicketOperation.UPDATE:
            spec = OperationSpec(
                op=op,
                route="/tickets/:TicketID",
                description="Update an existing ticket",
                methods=["PUT", "PATCH"],
                include_ticket_data="1",
            )
        else:
            continue
        operation_specs.append(spec)

    webservice_config = generator.generate_webservice_config(operation_specs)
    webservice_file = env.webservices_dir / f"{config.webservice_name}.yml"
    generator.save_to_file(webservice_config, webservice_file)

    # Install web service
    typer.echo(f"Installing web service from: {webservice_file}")
    result = console.add_webservice(config.webservice_name, webservice_file)
    if not result.ok:
        typer.echo(f"Failed to install web service: {result.err}", err=True)
        return

    typer.echo("✅ OTOBO system setup completed successfully!")

    # Generate client configuration
    base_url = "http://localhost/otobo/nph-genericinterface.pl/Webservice"
    OperationUrlMap(
        get_ticket=f"{base_url}/{config.webservice_name}/tickets/{{ticket_id}}",
        search_tickets=f"{base_url}/{config.webservice_name}/tickets/search",
        create_ticket=f"{base_url}/{config.webservice_name}/tickets",
        update_ticket=f"{base_url}/{config.webservice_name}/tickets/{{ticket_id}}",
    )

    typer.echo("\n📋 Client Configuration:")
    typer.echo(f"Base URL: {base_url}/{config.webservice_name}")
    typer.echo("Username: webservice")
    typer.echo(f"Password: {config.webservice_password}")
    typer.echo(f"Operations: {[op.value for op in config.enabled_operations]}")


@app.command()
def quick_setup(
        console_path: Path = typer.Option(Path("/opt/otobo/bin/otobo.Console.pl"), help="Path to OTOBO console"),
        webservices_dir: Path = typer.Option(Path("/opt/otobo/var/webservices"),
                                             help="Directory for web service files"),
        docker_container: str = typer.Option(None, help="Docker container name (if using Docker)"),
        webservice_name: str = typer.Option("PythonClientWebService", help="Name of the web service"),
        group_name: str = typer.Option("python-client-group", help="Name of the group to create"),
        user_name: str = typer.Option("python-client-user", help="Name of the user to create"),
        queue_name: str = typer.Option("Python Client Queue", help="Name of the queue to create"),
) -> None:
    """Quick setup for OTOBO system with sensible defaults."""

    # Determine environment
    if docker_container:
        env = DockerEnvironment(docker_container, "./bin/otobo.Console.pl", webservices_dir)
    else:
        env = SystemEnvironment(console_path, webservices_dir)

    # Create configuration
    config = SetupConfig(
        webservice_name=webservice_name,
        webservice_password=generate_random_password(),
        webservice_description="Web service for Python client integration",
        enabled_operations=[TicketOperation.GET, TicketOperation.SEARCH, TicketOperation.CREATE,
                            TicketOperation.UPDATE],

        group_name=group_name,
        group_comment="Group for Python client operations",

        user_name=user_name,
        user_first_name="Python",
        user_last_name="Client",
        user_email="python-client@example.com",
        user_password=generate_random_password(),
        user_permissions=["full"],

        queue_name=queue_name,
        queue_comment="Queue for tickets created via Python client",
    )

    setup_otobo_system(env, config)


if __name__ == "__main__":
    app()
