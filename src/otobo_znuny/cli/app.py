from __future__ import annotations

from typing import Iterable, List, Optional

import typer

from otobo_znuny.cli.environments import OtoboSystem, detect_system
from otobo_znuny.cli.otobo_console import OtoboConsole
from otobo_znuny.domain_models.ticket_operation import TicketOperation
from otobo_znuny.models.base_models import GroupConfig, QueueConfig, UserModel
from otobo_znuny.setup.bootstrap import generate_random_password, setup_otobo_system
from otobo_znuny.setup.config import SetupConfig

app = typer.Typer(help="Deprecated combined CLI. Prefer `otobo-cli` or `znuny-cli`.")

_ENV_CACHE: OtoboSystem | None = None


def _require_environment() -> OtoboSystem:
    global _ENV_CACHE
    if _ENV_CACHE is None:
        env = detect_system()
        if env is None:
            typer.echo(
                "Could not automatically detect an OTOBO/Znuny environment. "
                "Ensure the CLI is executed on the application host or inside its Docker container.",
                err=True,
            )
            raise typer.Exit(code=2)
        _ENV_CACHE = env
    return _ENV_CACHE


def _build_console() -> OtoboConsole:
    return OtoboConsole(_require_environment().build_command_runner())


def _resolve_operations(operation_names: Iterable[str]) -> list[TicketOperation]:
    operations: list[TicketOperation] = []
    for op_name in operation_names:
        try:
            operations.append(TicketOperation[op_name.upper()])
        except KeyError as exc:
            valid = ", ".join(member.name for member in TicketOperation)
            raise typer.BadParameter(f"Unknown operation '{op_name}'. Choose from: {valid}") from exc
    return operations


def _handle_result(result, success_message: str) -> None:
    if result.ok:
        typer.echo(success_message)
    else:
        typer.echo(result.err or "Operation failed", err=True)
        raise typer.Exit(code=result.code or 1)


@app.command("add-user")
def add_user(
    user_name: str = typer.Argument(...),
    first_name: str = typer.Argument(...),
    last_name: str = typer.Argument(...),
    email: str = typer.Argument(...),
    password: Optional[str] = typer.Option(None, "--password", "-p"),
    groups: Optional[List[str]] = typer.Option(None, "--group"),
) -> None:
    console = _build_console()
    final_password = password or typer.prompt("Password", hide_input=True, confirmation_prompt=True)
    user = UserModel(
        user_name=user_name,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=final_password,
        groups=groups or [],
    )
    _handle_result(console.add_user(user), f"User '{user_name}' created successfully.")


@app.command("add-group")
def add_group(
    group_name: str = typer.Argument(...),
    comment: Optional[str] = typer.Option(None, "--comment"),
) -> None:
    _handle_result(_build_console().add_group(GroupConfig(name=group_name, comment=comment)),
                   f"Group '{group_name}' created successfully.")


@app.command("link-user-to-group")
def link_user_to_group(
    user_name: str = typer.Argument(...),
    group_name: str = typer.Argument(...),
    permission: str = typer.Option("rw", "--permission", "-p"),
) -> None:
    _handle_result(
        _build_console().link_user_to_group(user_name, group_name, permission),
        f"Linked user '{user_name}' to group '{group_name}' with permission '{permission}'.",
    )


@app.command("add-queue")
def add_queue(
    name: str = typer.Argument(...),
    group: str = typer.Argument(...),
    comment: Optional[str] = typer.Option(None, "--comment"),
    system_address_id: Optional[int] = typer.Option(None, "--system-address-id"),
    system_address_name: Optional[str] = typer.Option(None, "--system-address-name"),
    unlock_timeout: Optional[int] = typer.Option(None, "--unlock-timeout"),
    first_response_time: Optional[int] = typer.Option(None, "--first-response-time"),
    update_time: Optional[int] = typer.Option(None, "--update-time"),
    solution_time: Optional[int] = typer.Option(None, "--solution-time"),
    calendar: Optional[int] = typer.Option(None, "--calendar"),
) -> None:
    queue = QueueConfig(
        name=name,
        group=group,
        system_address_id=system_address_id,
        system_address_name=system_address_name,
        comment=comment,
        unlock_timeout=unlock_timeout,
        first_response_time=first_response_time,
        update_time=update_time,
        solution_time=solution_time,
        calendar=calendar,
    )
    _handle_result(_build_console().add_queue(queue), f"Queue '{name}' created successfully.")


@app.command("list-queues")
def list_queues() -> None:
    result = _build_console().list_all_queues()
    if result.ok:
        typer.echo(result.out)
    else:
        typer.echo(f"Failed to list queues: {result.err}", err=True)
        raise typer.Exit(code=1)


@app.command("setup-otobo-znuny-system")
def interactive_setup() -> None:
    env = _require_environment()
    console = OtoboConsole(env.build_command_runner())
    typer.echo(f"Using environment: {env}")
    typer.echo("\n=== OTOBO/Znuny Webservice Setup ===\n")

    create_new_user = typer.confirm(
        "Do you want to create a new user specifically for the webservice? (Recommended)",
        default=True,
    )

    user = UserModel()
    user_users_permissions: list[str] = []
    webservice_restricted_user = None
    if create_new_user:
        user.user_name = typer.prompt("User login", default="python-client-user")
        user.first_name = typer.prompt("User first name", default="Python")
        user.last_name = typer.prompt("User last name", default="Client")
        user.email = typer.prompt("User email", default="python-client@example.com")
        user.password = typer.prompt(
            "User password",
            default=generate_random_password(),
            hide_input=True,
            confirmation_prompt=True,
        )
        while not console.is_strong_password(user.password):
            typer.echo("The provided password is too weak.", err=True)
            user.password = typer.prompt("User password", hide_input=True, confirmation_prompt=True)
        user_users_permissions = typer.prompt(
            f"What permissions to grant {user.user_name} on the 'users' group? ",
            default=["rw"],
        )
    else:
        restrict_webservice = typer.confirm(
            "Do you want to restrict the webservice to a specific user?"
        )
        if restrict_webservice:
            webservice_restricted_user = typer.prompt("Enter the username to restrict the webservice to")

    webservice_name = typer.prompt("Webservice name", default="PythonClientWebService")
    raw = typer.prompt(
        "Enabled webservice operations (comma separated)",
        default="GET,SEARCH,CREATE,UPDATE",
    )
    enabled_operations = _resolve_operations(part.strip() for part in raw.split(",") if part.strip())

    setup_otobo_system(
        env,
        SetupConfig(
            webservice_name=webservice_name,
            webservice_description="Webservice created by Otobo/Znuny Python Client CLI",
            enabled_operations=enabled_operations,
            user_to_add=user if create_new_user else None,
            user_users_permissions=user_users_permissions,
            _webservice_restricted_user=webservice_restricted_user,
            _restrict_webservice=webservice_restricted_user is not None,
        ),
    )


def run() -> None:
    app()


if __name__ == "__main__":
    run()
