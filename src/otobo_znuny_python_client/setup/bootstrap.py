from __future__ import annotations

import secrets
import string
import subprocess
from pathlib import Path
from typing import Callable, Iterable

from pydantic import BaseModel, ConfigDict

from otobo_znuny_python_client.cli.interface import OtoboCommandRunner, OtoboConsole
from otobo_znuny_python_client.domain_models.otobo_client_config import OperationUrlMap
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.builder import WebserviceBuilder

PermissionMap = {
    "owner": "owner",
    "move": "move_into",
    "priority": "priority",
    "create": "create",
    "read": "ro",
    "full": "rw",
}

DEFAULT_CONSOLE_PATHS = (
    Path("/opt/otobo/bin/otobo.Console.pl"),
    Path("/opt/znuny/bin/otrs.Console.pl"),
    Path("/opt/otrs/bin/otrs.Console.pl"),
)

DEFAULT_WEBSERVICE_PATHS = (
    Path("/opt/otobo/var/webservices"),
    Path("/opt/znuny/var/webservices"),
    Path("/opt/otrs/var/webservices"),
)

DEFAULT_DOCKER_CONTAINER_CANDIDATES = ("otobo-web-1", "otobo_web_1")
DEFAULT_DOCKER_CONSOLE_PATH = Path("/bin/otobo.Console.pl")
DEFAULT_DOCKER_WEBSERVICES_PATH = Path("/var/lib/docker/volumes/otobo_opt_otobo/_data/var/webservices")


def _get_running_container(candidates: Iterable[str]) -> str | None:
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    running = result.stdout.splitlines()
    for candidate in candidates:
        if any(candidate in name for name in running):
            return candidate
    return None


def _first_existing_path(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if Path(path).exists():
            return Path(path)
    return None


def detect_environment(
        *,
        console_paths: Iterable[Path] = DEFAULT_CONSOLE_PATHS,
        webservice_paths: Iterable[Path] = DEFAULT_WEBSERVICE_PATHS,
        docker_container_candidates: Iterable[str] = DEFAULT_DOCKER_CONTAINER_CANDIDATES,
        docker_console_path: Path = DEFAULT_DOCKER_CONSOLE_PATH,
        docker_webservices_path: Path = DEFAULT_DOCKER_WEBSERVICES_PATH,
) -> SystemEnvironment | DockerEnvironment | None:
    """Detect the active OTOBO/Znuny environment."""

    container_name = _get_running_container(docker_container_candidates)
    if container_name:
        return DockerEnvironment(
            container_name=container_name,
            console_path=str(docker_console_path),
            webservices_dir=docker_webservices_path,
        )

    console_path = _first_existing_path(console_paths)
    webservices_dir = _first_existing_path(webservice_paths)

    if console_path and webservices_dir:
        return SystemEnvironment(console_path=console_path, webservices_dir=webservices_dir)

    return None


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


def setup_otobo_system(
        env: SystemEnvironment | DockerEnvironment,
        config: SetupConfig,
        echo: Callable[[str], None] = print,
        echo_error: Callable[[str], None] | None = None,
) -> bool:
    """Set up OTOBO system with the provided configuration."""
    console = OtoboConsole(env.build_command_runner())

    err = echo_error or echo

    echo(f"Setting up OTOBO system using: {env}")

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
    webservice_file = env.webservices_dir / f"{config.webservice_name}.yml"
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
    OperationUrlMap(
        get_ticket=f"{base_url}/{config.webservice_name}/tickets/{{ticket_id}}",
        search_tickets=f"{base_url}/{config.webservice_name}/tickets/search",
        create_ticket=f"{base_url}/{config.webservice_name}/tickets",
        update_ticket=f"{base_url}/{config.webservice_name}/tickets/{{ticket_id}}",
    )

    echo("\n📋 Client Configuration:")
    echo(f"Base URL: {base_url}/{config.webservice_name}")
    echo("Username: webservice")
    echo(f"Password: {config.webservice_password}")
    echo(f"Operations: {[op.value for op in config.enabled_operations]}")

    return True
