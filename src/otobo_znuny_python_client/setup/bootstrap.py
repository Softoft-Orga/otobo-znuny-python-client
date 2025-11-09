from __future__ import annotations

import secrets
import string
from pathlib import Path
from typing import Callable

from cli.environments import OtoboSystem, DockerSystem, LocalSystem
from otobo_znuny_python_client import OtoboConsole
from .config import SetupConfig
from .webservices.builder import WebserviceBuilder


def generate_random_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def setup_otobo_system(
        system: OtoboSystem,
        config: SetupConfig,
        echo: Callable[[str], None] = print,
        echo_error: Callable[[str], None] | None = None,
) -> bool:
    """Set up OTOBO system with the provided configuration."""
    console = OtoboConsole(system.build_command_runner())

    err = echo_error or echo

    echo(f"Setting up OTOBO system using: {system}")

    if config.user_to_add:
        echo(f"Creating user: {config.user_to_add}")
        result = console.add_user(
            config.user_to_add
        )
        if not result.ok:
            err(f"Failed to create user: {result}")
            return False

        console.link_user_to_group_with_permissions(config.user_to_add.user_name, "users",
                                                    config.user_users_permissions)

    echo(f"Generating web service: {config.webservice_name}")

    builder = WebserviceBuilder(name=config.webservice_name)
    builder.enable_operations(*config.enabled_operations)

    if config.webservice_restricted_user:
        echo(f"Restricting webservice to user: {config.webservice_restricted_user}")
        builder.set_restricted_by(config.webservice_restricted_user)
    else:
        echo("⚠️  Webservice is NOT restricted to any specific user")

    webservice_config = builder.build()
    random_string = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    ramdom_file_name = f"{config.webservice_name}_{random_string}.yml"
    webservice_file = f"tmp/{ramdom_file_name}"
    builder.save_to_file(webservice_config, Path(webservice_file))

    if isinstance(system, DockerSystem):
        container_webservice_path = f"/opt/otobo/var/webservices/{config.webservice_name}.yml"
        echo(f"Copying web service to Docker container: {container_webservice_path}")
        if not system.copy_to_container(webservice_file, container_webservice_path):
            err("Failed to copy web service file to Docker container")
            return False
        result = console.add_webservice(config.webservice_name, container_webservice_path)

        echo(f"Installing web service from: {webservice_file}")

        if not result.ok:
            err(f"Failed to install web service: {result.err}")
            return False

    if isinstance(system, LocalSystem):
        container_webservice_path = f"/opt/otobo/var/webservices/{config.webservice_name}.yml"
        echo(f"Copying web service to Docker container: {container_webservice_path}")
        result = console.add_webservice(config.webservice_name, container_webservice_path)

        echo(f"Installing web service from: {webservice_file}")

        if not result.ok:
            err(f"Failed to install web service: {result.err}")
            return False

    echo("✅ OTOBO system setup completed successfully!")

    echo(f"Restricted to user: {config.webservice_restricted_user}")

    return True
