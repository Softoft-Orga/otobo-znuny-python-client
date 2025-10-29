from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

from cli import OtoboCommandRunner

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
    except Exception as e:
        print(f"Error while checking Docker containers: {e}")
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
) -> LocalSystem | DockerSystem | None:
    """Detect the active OTOBO/Znuny environment."""

    container_name = _get_running_container(docker_container_candidates)
    if container_name:
        return DockerSystem(
            container_name=container_name,
            console_path=docker_console_path,
            webservices_dir=docker_webservices_path,
        )

    console_path = _first_existing_path(console_paths)
    webservices_dir = _first_existing_path(webservice_paths)

    if console_path and webservices_dir:
        return LocalSystem(console_path=console_path, webservices_dir=webservices_dir)

    return None


class OtoboSystem(BaseModel):
    webservices_dir: Path
    console_path: Path

    def build_command_runner(self) -> OtoboCommandRunner:
        pass


class LocalSystem(OtoboSystem):
    def build_command_runner(self) -> OtoboCommandRunner:
        return OtoboCommandRunner.from_local(console_path=self.console_path)


class DockerSystem(OtoboSystem):
    container_name: str

    def build_command_runner(self) -> OtoboCommandRunner:
        return OtoboCommandRunner.from_docker(container=self.container_name, console_path=self.console_path)
