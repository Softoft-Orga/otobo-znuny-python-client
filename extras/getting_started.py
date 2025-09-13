"""Interactive helper to bootstrap OTOBO web services and user accounts."""
from __future__ import annotations

from pathlib import Path
import secrets
import string
from typing import Dict

from setup_webservices import WebServiceGenerator


OPERATIONS = {
    "get": "TicketGet",
    "search": "TicketSearch",
    "create": "TicketCreate",
    "update": "TicketUpdate",
}


def _ask_yes_no(prompt: str) -> bool:
    return input(prompt).strip().lower().startswith("y")



def _generate_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))



def main() -> None:
    base_url = input("Server base URL: ").strip()
    name = input("Webservice name (letters only): ").strip()
    ops_raw = input("Enable operations (comma separated: get,search,create,update): ").lower()
    ops_list = [o.strip() for o in ops_raw.split(",") if o.strip() in OPERATIONS]
    if not ops_list:
        print("No valid operations selected. Exiting.")
        return

    limit = _ask_yes_no("Restrict access to a single agent? (y/N): ")
    username = None
    if limit:
        username = input("Agent username: ").strip()
        fname = input("First name: ").strip()
        lname = input("Last name: ").strip()
        email = input("Email: ").strip()
        password = _generate_password()
        print(
            "\nCommand for creating the agent:\n"
            f"otobo.Console.pl Admin::User::Add --UserFirstname {fname} --UserLastname {lname} "
            f"--UserLogin {username} --UserPassword {password} --UserEmail {email}\n"
        )
    else:
        print("\nWarning: Access is not limited to a single agent. This may pose a security risk!\n")

    enabled_ops: Dict[str, None] = {OPERATIONS[o]: None for o in ops_list}
    generator = WebServiceGenerator()
    yaml_content = generator.generate_yaml(
        webservice_name=name,
        enabled_operations=enabled_ops,
        restricted_user=username,
    )
    config_file = Path(f"{name}.yml")
    config_file.write_text(yaml_content, encoding="utf-8")
    print(f"Webservice configuration written to {config_file}")
    print(
        "Command for adding the webservice:\n"
        f"otobo.Console.pl Admin::WebService::Add --Name {name} --Config {config_file}\n"
    )

    if _ask_yes_no("Store username and server address in .env file? (y/N): "):
        lines = [f"OTOBO_SERVER_URL={base_url}"]
        if username:
            lines.append(f"OTOBO_USERNAME={username}")
        Path(".env").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(
            "Created .env file (without password). "
            "Remember to set your password via the OTOBO_PASSWORD environment variable."
        )
    else:
        print(".env file not created.")


if __name__ == "__main__":
    main()
