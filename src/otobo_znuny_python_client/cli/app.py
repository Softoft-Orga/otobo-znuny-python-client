from __future__ import annotations

from typing import Iterable, List, Optional

import typer

from setup.bootstrap import setup_otobo_system
from setup.config import SetupConfig
from .command_models import Permission
from .environments import detect_system, OtoboSystem
from .otobo_console import OtoboConsole
from ..domain_models.ticket_operation import TicketOperation
from ..models.base_models import UserModel, GroupConfig, QueueConfig
from ..setup.bootstrap import generate_random_password

app = typer.Typer(help="Command line utilities for interacting with OTOBO/Znuny systems.")

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
    env = _require_environment()
    return OtoboConsole(env.build_command_runner())


def _resolve_operations(operation_names: Iterable[str]) -> list[TicketOperation]:
    operations: list[TicketOperation] = []
    for op_name in operation_names:
        try:
            operations.append(TicketOperation[op_name.upper()])
        except KeyError as exc:  # pragma: no cover - defensive guard
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
        user_name: str = typer.Argument(..., help="Login name of the new user."),
        first_name: str = typer.Argument(..., help="First name of the new user."),
        last_name: str = typer.Argument(..., help="Last name of the new user."),
        email: str = typer.Argument(..., help="Email address of the new user."),
        password: Optional[str] = typer.Option(None, "--password", "-p", help="Password for the new user."),
        groups: Optional[List[str]] = typer.Option(None, "--group", help="Group(s) to assign to the user."),
) -> None:
    console = _build_console()

    final_password = password or typer.prompt("Password", hide_input=True, confirmation_prompt=True)

    user = UserModel(
        user_name=user_name,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=final_password,
        groups=groups
    )

    result = console.add_user(user)
    _handle_result(result, f"User '{user_name}' created successfully.")


@app.command("add-group")
def add_group(
        group_name: str = typer.Argument(..., help="Name of the group."),
        comment: Optional[str] = typer.Option(None, "--comment", help="Optional comment for the group."),
) -> None:
    console = _build_console()

    group = GroupConfig(
        name=group_name,
        comment=comment
    )

    result = console.add_group(group)
    _handle_result(result, f"Group '{group_name}' created successfully.")


@app.command("link-user-to-group")
def link_user_to_group(
        user_name: str = typer.Argument(..., help="Existing user name."),
        group_name: str = typer.Argument(..., help="Existing group name."),
        permission: Permission | str = typer.Option("rw", "--permission", "-p",
                                                    help="Permission to grant to the user for the group."),
) -> None:
    console = _build_console()
    result = console.link_user_to_group(user_name, group_name, permission)
    _handle_result(result, f"Linked user '{user_name}' to group '{group_name}' with permission '{permission}'.")


@app.command("add-queue")
def add_queue(
        name: str = typer.Argument(..., help="Name of the queue."),
        group: str = typer.Argument(..., help="Group that owns the queue."),
        comment: Optional[str] = typer.Option(None, "--comment", help="Optional comment for the queue."),
        system_address_id: Optional[int] = typer.Option(None, "--system-address-id", help="System address identifier."),
        system_address_name: Optional[str] = typer.Option(None, "--system-address-name", help="System address name."),
        unlock_timeout: Optional[int] = typer.Option(None, "--unlock-timeout", help="Unlock timeout in minutes."),
        first_response_time: Optional[int] = typer.Option(None, "--first-response-time",
                                                          help="First response time in minutes."),
        update_time: Optional[int] = typer.Option(None, "--update-time", help="Update time in minutes."),
        solution_time: Optional[int] = typer.Option(None, "--solution-time", help="Solution time in minutes."),
        calendar: Optional[int] = typer.Option(None, "--calendar", help="Calendar identifier."),
) -> None:
    console = _build_console()

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

    result = console.add_queue(queue)
    _handle_result(result, f"Queue '{name}' created successfully.")


@app.command("list-queues")
def list_queues() -> None:
    """List all queues in the OTOBO/Znuny system."""
    console = _build_console()
    result = console.list_all_queues()
    if result.ok:
        typer.echo(result.out)
    else:
        typer.echo(f"Failed to list queues: {result.err}", err=True)
        raise typer.Exit(code=1)


def _prompt_operations(default: Iterable[TicketOperation]) -> list[TicketOperation]:
    default_str = ",".join(op.name for op in default)
    raw = typer.prompt(
        "Enabled webservice operations (comma separated)",
        default=default_str,
    )
    names = [part.strip() for part in raw.split(",") if part.strip()]
    return _resolve_operations(names)


def _prompt_permissions(default_permissions: Iterable[str]) -> list[str]:
    default_str = ",".join(default_permissions)
    raw = typer.prompt(
        "User permissions (comma separated: ro, move_into, create, owner, priority, rw)",
        default=default_str,
    )
    return [part.strip() for part in raw.split(",") if part.strip()]


@app.command("setup-otobo-znuny-system")
def interactive_setup() -> None:
    """
    Interactive setup for OTOBO/Znuny webservice configuration.

    This command guides you through creating:
    - A dedicated user for webservice access (recommended)
    - A webservice with configured operations
    """
    env = _require_environment()
    console = OtoboConsole(env.build_command_runner())

    typer.echo(f"Using environment: {env}")
    typer.echo("\n=== OTOBO/Znuny Webservice Setup ===\n")

    create_new_user = typer.confirm(
        "Do you want to create a new user specifically for the webservice? (Recommended)",
        default=True
    )

    user = UserModel()
    user_users_permissions = []
    webservice_restricted_user = None
    if create_new_user:
        typer.echo("\n--- User Configuration ---")

        user.user_name = typer.prompt("User login", default="python-client-user")
        user.first_name = typer.prompt("User first name", default="Python")
        user.last_name = typer.prompt("User last name", default="Client")
        user.email = typer.prompt("User email", default="python-client@example.com")
        user.password = typer.prompt(
            "User password",
            default=generate_random_password(),
            hide_input=True,
            confirmation_prompt=True
        )

        while not console.is_strong_password(user.password):
            typer.echo("The provided password is too weak. Please choose a stronger password.", err=True)
            user.password = typer.prompt(
                "User password",
                hide_input=True,
                confirmation_prompt=True
            )
        typer.echo("\n--- User Permissions ---")
        user_users_permissions = typer.prompt(
            f"What permissions to grant {user.user_name} on the 'users' group? ",
            default=["rw"]
        )

        typer.echo(f"Granting 'ro' permission on standard groups to {user.user_name}")

    else:
        typer.echo("\n--- Webservice Restriction Configuration ---")
        restrict_webservice = typer.confirm("Do you want to restrict the webservice to a specific user?\n"
                                            "(If yes, only that user can access the webservice endpoint)")

        if restrict_webservice:
            webservice_restricted_user = typer.prompt("Enter the username to restrict the webservice to")
        else:
            typer.echo("⚠️  Webservice will NOT be restricted to a specific user.")

    typer.echo("\n--- Webservice Configuration ---")
    webservice_name = typer.prompt("Webservice name", default="PythonClientWebService")
    enabled_operations = _prompt_operations(
        [TicketOperation.GET, TicketOperation.SEARCH, TicketOperation.CREATE, TicketOperation.UPDATE]
    )

    setup_otobo_system(
        env,
        SetupConfig(
            webservice_name=webservice_name,
            webservice_description="Webservice created by Otobo/Znuny Python Client CLI",
            enabled_operations=enabled_operations,
            user_to_add=user,
            user_users_permissions=user_users_permissions,
            _webservice_restricted_user=webservice_restricted_user,
            _restrict_webservice=webservice_restricted_user is not None,
        )
    )


def run() -> None:
    """Entry point for execution via ``python -m``."""
    app()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run()
