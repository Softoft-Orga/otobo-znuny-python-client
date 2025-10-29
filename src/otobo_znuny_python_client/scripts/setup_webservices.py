from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer

from otobo_znuny_python_client.setup.webservices import (
    DEFAULT_FRAMEWORK_VERSION,
    WebserviceBuilder,
    generate_enabled_operations_list,
)
from otobo_znuny_python_client.setup.webservices.operations import SUPPORTED_OPERATIONS_DOC

RESTRICTION_DOC = (
    "Use --restrict-user to bind the webservice to a dedicated agent account. "
    "Omit the option to allow any authenticated agent."
)

CLI_DESCRIPTION = "\n\n".join([
    "Generate OTOBO/Znuny webservice YAML.",
    SUPPORTED_OPERATIONS_DOC,
    RESTRICTION_DOC,
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


@app.command(help="\n\n".join([SUPPORTED_OPERATIONS_DOC, RESTRICTION_DOC]))
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
        restrict_user: Annotated[
            str | None,
            typer.Option(
                "--restrict-user",
                metavar="USERNAME",
                rich_help_panel="Access",
                help="Restrict the webservice to a dedicated agent login.",
            ),
        ] = None,
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

    enabled_operations = generate_enabled_operations_list(enabled_operations_raw)
    if not enabled_operations:
        typer.secho("Error: No valid operations specified.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    builder = WebserviceBuilder(name=validated_name, framework_version=version)
    if restrict_user:
        builder.set_restricted_by(restrict_user)
    for operation in enabled_operations:
        builder.enable_operation(operation)

    try:
        config = builder.build()
    except ValueError as exc:  # pragma: no cover - defensive
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if file:
        builder.save_to_file(config, file)
        typer.secho(
            "Successfully generated webservice configuration.", fg=typer.colors.GREEN,
        )
        typer.secho(f"File: {file}")
    else:
        typer.secho("--- Generated YAML ---", bold=True)
        typer.echo(builder.dump_yaml(config))


if __name__ == "__main__":
    app()
