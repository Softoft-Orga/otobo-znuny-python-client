import shlex
import subprocess
import time
from pathlib import Path

from cli.environments import detect_system
from models import UserModel
from otobo_znuny_python_client import TicketOperation, OtoboConsole
from setup.bootstrap import setup_otobo_system
from setup.config import SetupConfig


def run(cmd: list[str]):
    subprocess.run(cmd, check=True, text=True)


def compose(compose_path: Path, args: str):
    run(["docker", "compose", "-f", str(compose_path), *shlex.split(args)])


def recreate_local_test_system():
    compose_path = Path(__file__).parent / "otobo-docker" / "compose.yml"
    compose(compose_path, "down -v --remove-orphans")
    compose(compose_path, "build --no-cache")
    compose(compose_path, "up -d")
    time.sleep(10)
    compose(compose_path,
            'exec web bash -lc "rm -f Kernel/Config/Files/ZZZAAuto.pm && bin/docker/quick_setup.pl --db-password 1234"')
    setup_otobo_system(detect_system(),
                       SetupConfig(webservice_name="OpenTicketAI",
                                   webservice_description="Web service for OpenTicketAI integration",
                                   enabled_operations=list(TicketOperation),
                                   user_to_add=UserModel(user_name="otobo_user",
                                                         first_name="Otobo",
                                                         last_name="User",
                                                         email="tab@softoft.de",
                                                         password="S2ram!_heziiquwrbssdf3382HAAngP@ssw0rd!"),
                                   user_users_permissions=["ro", "move_into", "create", "owner", "priority", "rw"],
                                   )

                       )
    console = OtoboConsole(detect_system().build_command_runner())
    console.add_user(
        UserModel(user_name="admin",
                  first_name="Otobo",
                  last_name="User",
                  email="tab@softoft.de",
                  password="sublevel-concise-stalemate")
    )
    console.link_user_to_group_with_permissions(
        "admin",
        "admin",
        ["ro", "move_into", "create", "owner", "priority", "rw"],
    )
    console.link_user_to_group_with_permissions(
        "admin",
        "users",
        ["ro", "move_into", "create", "owner", "priority", "rw"],
    )


if __name__ == "__main__":
    recreate_local_test_system()
