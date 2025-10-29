from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer

from otobo_znuny_python_client.setup.webservices import (
    AUTH_EXPECTATIONS_DOC,
    DEFAULT_BASIC_AUTH_PASSWORD,
    DEFAULT_BASIC_AUTH_USER,
    DEFAULT_FRAMEWORK_VERSION,
    WebServiceGenerator,
    generate_enabled_operations_list,
)
from setup.webservices import SUPPORTED_OPERATIONS_DOC

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


def _validate_name(name: str) -> str:
    if not name:
        raise typer.BadParameter("Webservice name cannot be empty.")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
        raise typer.BadParameter(
            "Name must start with a letter and contain only A–Z, a–z, 0–9, _ or -.",
        )
    return name


@app.command(help="\n\n".join([SUPPORTED_OPERATIONS_DOC, AUTH_EXPECTATIONS_DOC]))
def generate(
        name: Annotated[str, typer.Option("--name", rich_help_panel="Required")],
        enabled_operations_raw: Annotated[
            list[str],
            typer.Option(
                "--op",
                "-o",
                help="Repeat for each: get, search, create, update",
                case_sensitive=False,
                rich_help_panel="Operations",
            ),
        ],
        allow_user: Annotated[
            str | None,
            typer.Option(
                "--allow-user",
                metavar="USERNAME",
                rich_help_panel="Auth",
                help="Limit access to a dedicated agent user (sets BasicAuth user).",
            ),
        ] = None,
        allow_all_agents: Annotated[
            bool,
            typer.Option(
                "--allow-all-agents",
                rich_help_panel="Auth",
                help="Allow any authenticated agent (uses shared BasicAuth user).",
            ),
        ] = False,
        password: Annotated[
            str,
            typer.Option(
                "--password",
                rich_help_panel="Auth",
                help="Password assigned to the BasicAuth user.",
            ),
        ] = DEFAULT_BASIC_AUTH_PASSWORD,
        version: Annotated[
            str,
            typer.Option("--version", rich_help_panel="Optional"),
        ] = DEFAULT_FRAMEWORK_VERSION,
        file: Annotated[
            Path | None,
            typer.Option("--file", metavar="FILENAME", rich_help_panel="Output"),
        ] = None,
) -> None:
    try:
        validated_name = _validate_name(name)
    except typer.BadParameter as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    if not (allow_user or allow_all_agents):
        typer.secho(
            "Error: You must specify an authentication mode.", fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    if allow_user and allow_all_agents:
        typer.secho(
            "Error: --allow-user and --allow-all-agents are mutually exclusive.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    enabled_operations = generate_enabled_operations_list(enabled_operations_raw)
    if not enabled_operations:
        typer.secho("Error: No valid operations specified.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    description = WebServiceGenerator.build_description(
        name=validated_name,
        restricted_user=allow_user,
        allow_all_agents=allow_all_agents,
    )
    generator = WebServiceGenerator(
        name=validated_name,
        description=description,
        framework_version=version,
        basic_auth_user=allow_user or DEFAULT_BASIC_AUTH_USER,
        basic_auth_password=password,
    )

    config = generator.build_config(enabled_operations)

    if file:
        generator.save_to_file(config, file)
        typer.secho(
            "Successfully generated webservice configuration.", fg=typer.colors.GREEN,
        )
        typer.secho(f"File: {file}")
    else:
        typer.secho("--- Generated YAML ---", bold=True)
        typer.echo(generator.dump_yaml(config))


if __name__ == "__main__":
    app()
