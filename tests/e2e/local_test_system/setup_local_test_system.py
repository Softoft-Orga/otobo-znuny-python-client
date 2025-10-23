import subprocess
import time
from pathlib import Path

from otobo_znuny_python_client.cli.interface import OtoboCommandRunner, OtoboConsole


def run_docker_compose_command(cmd: str, compose_path: Path):
    subprocess.run(["docker", "compose", "-f", compose_path, cmd], capture_output=True, text=True)


def _run_command(cmd):
    subprocess.run(cmd, capture_output=True, text=True)


def create_local_test_system():
    compose_path = Path(__file__).parent / "otobo-docker" / "compose.yml"
    run_docker_compose_command("up -d --wait", compose_path)
    time.sleep(2)
    run_docker_compose_command(
        'exec web bash -c "rm -f Kernel/Config/Files/ZZZAAuto.pm ; bin/docker/quick_setup.pl --db-password 1234"',
        compose_path)
    OtoboConsole(OtoboCommandRunner.from_docker())


if __name__ == "__main__":
    create_local_test_system()
