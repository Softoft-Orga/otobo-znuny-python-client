from __future__ import annotations

from pathlib import Path

from otrs_gi_core.cli.environments import (
    DockerSystem,
    HostSystem,
    LocalSystem,
    detect_system as _detect_system,
)
from otrs_gi_core.cli.command_runner import ConsoleCommandRunner as OtoboCommandRunner

OtoboSystem = HostSystem

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
DEFAULT_DOCKER_CONTAINER_CANDIDATES = ("otobo-web-1", "otobo_web_1", "znuny-web-1", "znuny_web_1")
DEFAULT_DOCKER_CONSOLE_PATH = "/opt/otobo/bin/otobo.Console.pl"
DEFAULT_DOCKER_WEBSERVICES_PATH = Path(
    "/var/lib/docker/volumes/otobo_opt_otobo/_data/var/webservices"
)


def detect_system():
    return _detect_system(
        console_paths=DEFAULT_CONSOLE_PATHS,
        webservice_paths=DEFAULT_WEBSERVICE_PATHS,
        docker_container_candidates=DEFAULT_DOCKER_CONTAINER_CANDIDATES,
        docker_console_path=DEFAULT_DOCKER_CONSOLE_PATH,
        docker_webservices_path=DEFAULT_DOCKER_WEBSERVICES_PATH,
    )


__all__ = [
    "DockerSystem",
    "LocalSystem",
    "OtoboCommandRunner",
    "OtoboSystem",
    "detect_system",
]
