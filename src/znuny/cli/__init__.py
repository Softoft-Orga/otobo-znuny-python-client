from znuny.cli.environments import detect_znuny_system
from otrs_gi_core.cli.app_factory import create_cli_app

app = create_cli_app(product_label="Znuny", detect_environment=detect_znuny_system)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
