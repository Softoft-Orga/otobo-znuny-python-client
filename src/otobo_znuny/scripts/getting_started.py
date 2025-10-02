from __future__ import annotations

import secrets
import string

import typer
from pydantic import BaseModel, ConfigDict
from pathlib import Path
import subprocess
from typing import Optional, Union

from otobo_znuny.domain_models.otobo_client_config import OperationUrlMap
from otobo_znuny.domain_models.ticket_operation import TicketOperation
from otobo_znuny.scripts.cli_interface import OtoboConsole, CommandRunner
from otobo_znuny.scripts.setup_webservices import WebServiceGenerator

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

    # Read existing lines
    if rc_file.exists():
        lines = rc_file.read_text().splitlines()
    else:
        lines = []

    # Remove old definition if present
    lines = [line for line in lines if not line.strip().startswith(f"export {key}=")]
    lines.append(export_line.strip())

    # Write back
    rc_file.write_text("\n".join(lines) + "\n")

    # Apply immediately for current session
    subprocess.run(f"export {key}='{value}'", shell=True, executable="/bin/bash")


class SystemEnvironment:
    def __init__(self, console_path: Path, webservices_dir: Path):
        self.console_path = console_path
        self.webservices_dir = webservices_dir

    def build_command_runner(self) -> CommandRunner:
        return CommandRunner.from_local(console_path=self.console_path)

    def __str__(self) -> str:
        return f"SystemEnvironment(console_path={self.console_path}, webservices_dir={self.webservices_dir})"

    def is_valid_environment(self) -> bool:
        return self.console_path.exists() and self.webservices_dir.exists()

    @property
    def ticket_system_name(self):
        if "otobo" in str(self.console_path).lower():
            return "otobo"
        elif "znuny" in str(self.console_path).lower():
            return "znuny"
        elif "otrs" in str(self.console_path).lower():
            return "otrs"
        else:
            return "Unknown"


class DockerEnvironment(SystemEnvironment):
    def __init__(self, container_name: str, console_path: Path,
                 webservices_dir):
        super().__init__(
            console_path=console_path,
            webservices_dir=webservices_dir
        )
        self.container_name = container_name

    def build_command_runner(self) -> CommandRunner:
        return CommandRunner.from_docker(container=self.container_name, console_path=self.console_path)

    def __str__(self) -> str:
        return f"DockerEnvironment(container_name={self.container_name}, console_path={self.console_path}, webservices_dir={self.webservices_dir})"

    def is_valid_environment(self) -> bool:
        return self.webservices_dir.exists()


def _slug(s: str) -> str:
    keep = string.ascii_letters + string.digits + "-"
    s2 = "".join(ch if ch in keep else "-" for ch in s.strip().replace(" ", "-"))
    s2 = s2.strip("-").lower()
    while "--" in s2:
        s2 = s2.replace("--", "-")
    return s2


def _gen_random_domain() -> str:
    name = _gen_password(8).lower()
    return f"{name}.com"


def _gen_password(n: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def _write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _get_running_container(name_patterns: list[str]) -> Optional[str]:
    try:
        out = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=5)
        if out.returncode != 0:
            return None
        output_names = out.stdout.splitlines()
        for name in name_patterns:
            if any([name in n for n in output_names]):
                return name
    except Exception:
        return None
    return None


CONSOLE_PATHS = [
    Path("/opt/otobo/bin/otobo.Console.pl"),
    Path("/opt/znuny/bin/otrs.Console.pl"),
    Path("/opt/otrs/bin/otrs.Console.pl")
]

WEBSERVICES_PATHS = [
    Path("/opt/otobo/var/webservices"),
    Path("/opt/znuny/var/webservices"),
    Path("/opt/otrs/var/webservices"),
]

OTOBO_DOCKER_WEBSERVICE_PATH = Path("/var/lib/docker/volumes/otobo_opt_otobo/_data/var/webservices")


def _build_system_environment(console_path: Path, webservices_dir: Path,
                              container_name: Optional[str] = None) -> SystemEnvironment:
    if container_name:
        return DockerEnvironment(container_name=container_name, console_path=console_path,
                                 webservices_dir=webservices_dir)
    return SystemEnvironment(console_path=console_path, webservices_dir=webservices_dir)


def _detect_environment() -> Optional[SystemEnvironment]:
    container_name = _get_running_container(["otobo-web-1", "otobo_web_1"])
    if container_name:
        return DockerEnvironment(container_name=container_name, console_path=Path("/bin/otobo.Console.pl"),
                                 webservices_dir=OTOBO_DOCKER_WEBSERVICE_PATH)
    correct_console_paths = [console_path for console_path in CONSOLE_PATHS if console_path.exists()]
    correct_ws_paths = [ws_path for ws_path in WEBSERVICES_PATHS if ws_path.exists()]
    if len(correct_console_paths) == 1 and len(correct_ws_paths) == 1:
        return SystemEnvironment(console_path=correct_console_paths[0], webservices_dir=correct_ws_paths[0])
    return None


class GettingStartedConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_url: Optional[str] = None
    env_kind: Optional[SystemEnvironment] = None
    webservice_name: Optional[str] = None
    username: Optional[str] = None
    user_password_env: Optional[str] = None
    queue_name: Optional[str] = None
    group_name: Optional[str] = None
    ops: Optional[OperationUrlMap] = None
    ws_file: Optional[Path] = None


class GettingStarted:
    def __init__(self):
        self.config = GettingStartedConfig()
        self.console: Optional[OtoboConsole] = None
        self.system_environment: Optional[SystemEnvironment] = None

    def _manually_select_environment(self) -> Optional[SystemEnvironment]:
        typer.echo("Could not automatically detect OTOBO environment.")
        use_docker = typer.confirm("Are you using OTOBO in Docker?")

        if use_docker:
            container_name = typer.prompt(
                "Container name (In normal installation either otobo-web-1 or otobo_web_1",
                default="otobo-web-1"
            )
            console_path = Path(typer.prompt("Console path inside container", default="/bin/otobo.Console.pl"))
            webservices_dir = Path(
                typer.prompt("Webservices directory full absolute path from host",
                             default=OTOBO_DOCKER_WEBSERVICE_PATH))
            env = DockerEnvironment(container_name=container_name, console_path=console_path,
                                    webservices_dir=webservices_dir)
            if not env.is_valid_environment():
                typer.echo(f"Invalid Docker environment: {env}")
                return None
            return env
        else:
            console_path = Path(typer.prompt("Console path", default="/opt/otobo/bin/otobo.Console.pl"))
            webservices_dir = Path(typer.prompt("Webservices directory", default="/opt/otobo/var/webservices"))
            env = SystemEnvironment(console_path=console_path, webservices_dir=webservices_dir)
            if not env.is_valid_environment():
                typer.echo(f"Invalid local environment: {env}")
                return None
            return env

    def _create_user(self):
        create_user = typer.confirm("Create a new user for Open Ticket AI?", default=True)
        if create_user:
            username = typer.prompt("Login", default="open_ticket_ai")
            user_first = typer.prompt("First name", default="Open Ticket")
            user_last = typer.prompt("Last name", default="AI")
            user_email = typer.prompt("Email")
            user_password = _gen_password()
            cmd_result = self.console.add_user(
                user_name=username,
                first_name=user_first,
                last_name=user_last,
                email_address=user_email,
                password=user_password
            )
            if not cmd_result.ok:
                typer.echo(f"Error creating user: {cmd_result.err}")
                raise typer.Exit(code=1)
        else:
            username = typer.prompt("Existing login")
            user_password = typer.prompt("Password for existing user", hide_input=True)

        self.config.username = username
        self.config.user_password_env = "OTOBO_PASSWORD"
        set_env_var("OTOBO_PASSWORD", user_password)

    def run(self) -> None:
        self.system_environment = _detect_environment()
        if not self.system_environment or not self.system_environment.is_valid_environment():
            self._manually_select_environment()
        self.console = OtoboConsole(self.system_environment.build_command_runner())
        typer.echo(f"Detected: {self.system_environment}")
        self._create_user()
        webservice_url = typer.prompt("Generic Interface URL",
                                      default=f"http://localhost/{self.system_environment.ticket_system_name}/"
                                              f"nph-genericinterface.pl")
        ws_name = typer.prompt("Webservice name", default="OpenTicketAI")

        queue_name = typer.prompt("Incoming tickets queue", default="Incoming Tickets")
        group_name = typer.prompt("Queue group (create if missing)", default="users")
        self.console.add_group(group_name)
        self.console.add_queue(name=queue_name, group=group_name)
        self.console.link_user_to_group(user_name=self.config.username, group_name=group_name,
                                        permission=str(PermissionMap["full"]))
        ops_choices = [
            (TicketOperation.CREATE, True),
            (TicketOperation.UPDATE, True),
            (TicketOperation.SEARCH, True),
            (TicketOperation.GET, True),
        ]
        ops = []
        for op, d in ops_choices:
            if typer.confirm(f"Enable {op}?", default=d):
                ops.append(op)
        WebServiceGenerator().write_yaml_to_file(
            restricted_user=self.config.username,
            webservice_name=self.config.webservice_name,
            enabled_operations=ops,
            file_path=self.system_environment.webservices_dir / f"{ws_name}.yml",
        )
        cfg_yaml = Path("config.yaml")
        cfg_yaml.write_text(self.config.model_dump())


@app.command()
def getting_started():
    GettingStarted().run()


if __name__ == "__main__":
    app()
