from __future__ import annotations

from pathlib import Path

from otrs_gi_core.cli.environments import HostSystem, detect_system

DEFAULT_CONSOLE_PATHS = (
    Path("/opt/znuny/bin/otrs.Console.pl"),
    Path("/opt/otrs/bin/otrs.Console.pl"),
)
DEFAULT_WEBSERVICE_PATHS = (
    Path("/opt/znuny/var/webservices"),
    Path("/opt/otrs/var/webservices"),
)
DEFAULT_DOCKER_CONTAINER_CANDIDATES = ("znuny-web-1", "znuny_web_1", "otrs-web-1")
DEFAULT_DOCKER_CONSOLE_PATH = "/opt/znuny/bin/otrs.Console.pl"
DEFAULT_DOCKER_WEBSERVICES_PATH = Path("/opt/znuny/var/webservices")


def detect_znuny_system() -> HostSystem | None:
    return detect_system(
        console_paths=DEFAULT_CONSOLE_PATHS,
        webservice_paths=DEFAULT_WEBSERVICE_PATHS,
        docker_container_candidates=DEFAULT_DOCKER_CONTAINER_CANDIDATES,
        docker_console_path=DEFAULT_DOCKER_CONSOLE_PATH,
        docker_webservices_path=DEFAULT_DOCKER_WEBSERVICES_PATH,
    )
