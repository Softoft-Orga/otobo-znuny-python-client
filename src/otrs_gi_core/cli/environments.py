from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

from otrs_gi_core.cli.command_runner import ConsoleCommandRunner


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


def detect_system(
    *,
    console_paths: Iterable[Path],
    webservice_paths: Iterable[Path],
    docker_container_candidates: Iterable[str],
    docker_console_path: str,
    docker_webservices_path: Path,
) -> HostSystem | None:
    """Detect a local or Docker OTRS-family environment."""

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
        return LocalSystem(console_path=str(console_path), webservices_dir=webservices_dir)

    return None


class HostSystem(BaseModel):
    webservices_dir: Path
    console_path: str

    def build_command_runner(self) -> ConsoleCommandRunner:
        raise NotImplementedError

    @property
    def container_webservice_dir(self) -> str:
        return str(self.webservices_dir)


class LocalSystem(HostSystem):
    def build_command_runner(self) -> ConsoleCommandRunner:
        return ConsoleCommandRunner.from_local(console_path=self.console_path)


class DockerSystem(HostSystem):
    container_name: str

    def build_command_runner(self) -> ConsoleCommandRunner:
        return ConsoleCommandRunner.from_docker(
            container=self.container_name,
            console_path=self.console_path,
        )

    def copy_to_container(self, source_path: str, container_path: str) -> bool:
        args = ["docker", "cp", source_path, f"{self.container_name}:{container_path}"]
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            print(f"Error copying file to container: {result.stderr}")
            return False
        return True
