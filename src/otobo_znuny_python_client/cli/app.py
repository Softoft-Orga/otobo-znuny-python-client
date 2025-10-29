from __future__ import annotations

from typing import Iterable, List, Optional

import typer

from otobo_znuny_python_client.cli.interface import OtoboConsole, Permission
from otobo_znuny_python_client.cli.webservice_factory import create_webservice
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.bootstrap import (
    DockerEnvironment,
    SetupConfig,
    SystemEnvironment,
    detect_environment,
    generate_random_password,
    setup_otobo_system,
)


app = typer.Typer(help="Command line utilities for interacting with OTOBO/Znuny systems.")


_ENV_CACHE: SystemEnvironment | DockerEnvironment | None = None


def _require_environment() -> SystemEnvironment | DockerEnvironment:
    global _ENV_CACHE
    if _ENV_CACHE is None:
        env = detect_environment()
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
    result = console.add_user(user_name, first_name, last_name, email, final_password, groups)
    _handle_result(result, f"User '{user_name}' created successfully.")


@app.command("add-group")
def add_group(
        group_name: str = typer.Argument(..., help="Name of the group."),
        comment: Optional[str] = typer.Option(None, "--comment", help="Optional comment for the group."),
) -> None:
    console = _build_console()
    result = console.add_group(group_name, comment)
    _handle_result(result, f"Group '{group_name}' created successfully.")


@app.command("link-user-to-group")
def link_user_to_group(
        user_name: str = typer.Argument(..., help="Existing user name."),
        group_name: str = typer.Argument(..., help="Existing group name."),
        permission: Permission | str = typer.Option("rw", "--permission", "-p", help="Permission to grant to the user for the group."),
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
        first_response_time: Optional[int] = typer.Option(None, "--first-response-time", help="First response time in minutes."),
        update_time: Optional[int] = typer.Option(None, "--update-time", help="Update time in minutes."),
        solution_time: Optional[int] = typer.Option(None, "--solution-time", help="Solution time in minutes."),
        calendar: Optional[int] = typer.Option(None, "--calendar", help="Calendar identifier."),
) -> None:
    console = _build_console()
    result = console.add_queue(
        name,
        group,
        system_address_id=system_address_id,
        system_address_name=system_address_name,
        comment=comment,
        unlock_timeout=unlock_timeout,
        first_response_time=first_response_time,
        update_time=update_time,
        solution_time=solution_time,
        calendar=calendar,
    )
    _handle_result(result, f"Queue '{name}' created successfully.")


@app.command("setup-webservice")
def setup_webservice(
        webservice_name: str = typer.Argument(..., help="Name of the webservice."),
        enabled_operations: Optional[List[str]] = typer.Option(None, "--operation", "-o", help="Enabled ticket operations (e.g. GET, CREATE)."),
        restriction_by_user: Optional[str] = typer.Option(None, "--restriction-by-user", help="Optional username to restrict the webservice to."),
) -> None:
    operations = _resolve_operations(enabled_operations or [])
    create_webservice(webservice_name, operations, restriction_by_user)
    typer.echo(f"Webservice '{webservice_name}' prepared with operations {[op.name for op in operations]}.")


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
    env = _require_environment()
    typer.echo(f"Using environment: {env}")

    group_name = typer.prompt("Group name", default="python-client-group")
    group_comment = typer.prompt("Group comment", default="Group for Python client operations")

    user_name = typer.prompt("User login", default="python-client-user")
    user_first_name = typer.prompt("User first name", default="Python")
    user_last_name = typer.prompt("User last name", default="Client")
    user_email = typer.prompt("User email", default="python-client@example.com")
    user_password = typer.prompt("User password", default=generate_random_password(), hide_input=True, confirmation_prompt=True)
    user_permissions = _prompt_permissions(["rw"])

    queue_name = typer.prompt("Queue name", default="Python Client Queue")
    queue_comment = typer.prompt("Queue comment", default="Queue for tickets created via Python client")

    webservice_name = typer.prompt("Webservice name", default="PythonClientWebService")
    webservice_description = typer.prompt("Webservice description", default="Web service for Python client integration")
    webservice_password = typer.prompt("Webservice password", default=generate_random_password(), hide_input=True, confirmation_prompt=True)
    enabled_operations = _prompt_operations(
        [TicketOperation.GET, TicketOperation.SEARCH, TicketOperation.CREATE, TicketOperation.UPDATE]
    )

    config = SetupConfig(
        webservice_name=webservice_name,
        webservice_password=webservice_password,
        webservice_description=webservice_description,
        enabled_operations=enabled_operations,
        group_name=group_name,
        group_comment=group_comment,
        user_name=user_name,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        user_email=user_email,
        user_password=user_password,
        user_permissions=user_permissions,
        queue_name=queue_name,
        queue_comment=queue_comment,
    )

    success = setup_otobo_system(
        env,
        config,
        echo=typer.echo,
        echo_error=lambda message: typer.echo(message, err=True),
    )

    if not success:
        raise typer.Exit(code=1)


def run() -> None:
    """Entry point for execution via ``python -m``."""
    app()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run()
