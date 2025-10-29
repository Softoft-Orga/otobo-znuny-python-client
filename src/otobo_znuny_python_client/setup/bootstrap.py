from __future__ import annotations

import secrets
import string
from typing import Callable

from .config import SetupConfig
from .webservices.builder import WebserviceBuilder
from ..cli.environments import OtoboSystem
from ..cli.otobo_console import OtoboConsole

PermissionMap = {
    "owner": "owner",
    "move": "move_into",
    "priority": "priority",
    "create": "create",
    "read": "ro",
    "full": "rw",
}


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

    # Create group
    echo(f"Creating group: {config.group_name}")
    result = console.add_group(config.group_name, config.group_comment)
    if not result.ok:
        err(f"Failed to create group: {result.err}")
        return False

    # Create user
    echo(f"Creating user: {config.user_name}")
    result = console.add_user(
        config.user_name,
        config.user_first_name,
        config.user_last_name,
        config.user_email,
        config.user_password,
    )
    if not result.ok:
        err(f"Failed to create user: {result.err}")
        return False

    # Link user to group with permissions
    for permission in config.user_permissions:
        mapped_permission = PermissionMap.get(permission, permission)
        echo(f"Linking user {config.user_name} to group {config.group_name} with {mapped_permission} permission")
        result = console.link_user_to_group(config.user_name, config.group_name, mapped_permission)
        if not result.ok:
            err(f"Failed to link user to group: {result.err}")

    # Create queue
    echo(f"Creating queue: {config.queue_name}")
    result = console.add_queue(config.queue_name, config.group_name, comment=config.queue_comment)
    if not result.ok:
        err(f"Failed to create queue: {result.err}")
        return False

    # Generate and install web service
    echo(f"Generating web service: {config.webservice_name}")

    builder = WebserviceBuilder(name=config.webservice_name)
    builder.enable_operations(*config.enabled_operations)
    builder.set_restricted_by(config.user_name)

    webservice_config = builder.build()
    webservice_file = system.webservices_dir / f"{config.webservice_name}.yml"
    builder.save_to_file(webservice_config, webservice_file)

    # Install web service
    echo(f"Installing web service from: {webservice_file}")
    result = console.add_webservice(config.webservice_name, webservice_file)
    if not result.ok:
        err(f"Failed to install web service: {result.err}")
        return False

    echo("✅ OTOBO system setup completed successfully!")

    # Generate client configuration
    base_url = "http://localhost/otobo/nph-genericinterface.pl/Webservice"

    echo("\n📋 Client Configuration:")
    echo(f"Base URL: {base_url}/{config.webservice_name}")
    echo(f"Operations: {[op.value for op in config.enabled_operations]}")

    return True
