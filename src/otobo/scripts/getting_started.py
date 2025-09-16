#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import secrets
import string
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests
import typer

from setup_webservices import WebServiceGenerator

app = typer.Typer(add_completion=False, context_settings={"help_option_names": ["-h", "--help"]})

OPERATIONS: Dict[str, str] = {
    "get": "TicketGet",
    "search": "TicketSearch",
    "create": "TicketCreate",
    "update": "TicketUpdate",
}


def _generate_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _slug(s: str) -> str:
    s2 = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s2 or "ws"


def _email_local(s: str) -> str:
    return re.sub(r"[^a-z0-9._+-]", "", s.lower())


def _write_file(path: Path, data: str, force: bool) -> None:
    if path.exists() and not force:
        typer.secho(f"File exists: {path}. Use --force to overwrite.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    path.write_text(data, encoding="utf-8")
    typer.secho(f"Wrote {path}", fg=typer.colors.GREEN)


def _prompt_yes(msg: str, default: bool = True) -> bool:
    return typer.confirm(msg, default=default)


def _http_post(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(url, json=payload, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"status": r.status_code, "text": r.text}


@app.command()
def bootstrap(
        base_url: str = typer.Option(..., "--base-url", "-u",
                                     help="Server base URL, e.g. http://host/otobo/nph-genericinterface.pl"),
        name: str = typer.Option(..., "--name", "-n", help="Webservice name (letters, numbers, dashes)"),
        op: List[str] = typer.Option(..., "--op", "-o", help="Repeat for each: get, search, create, update",
                                     case_sensitive=False),
        restrict_user: Optional[str] = typer.Option(None, "--user", help="Agent login to restrict access to"),
        first_name: Optional[str] = typer.Option(None, "--first-name"),
        last_name: Optional[str] = typer.Option(None, "--last-name"),
        email: Optional[str] = typer.Option(None, "--email"),
        version: str = typer.Option("11.0.0", "--version", help="FrameworkVersion"),
        out: Optional[Path] = typer.Option(None, "--out", "-f", help="Output YAML file; defaults to <name>.yml"),
        write_env: bool = typer.Option(False, "--write-env/--no-write-env", help="Write .env with server and username"),
        env_file: Path = typer.Option(Path(".env"), "--env-file"),
        force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
        run_test: bool = typer.Option(True, "--test", help="Attempt live HTTP test after setup"),
):
    ops_clean = [s.lower().strip() for s in op if s.lower().strip() in OPERATIONS]
    if not ops_clean:
        typer.secho("No valid operations provided.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    slug_name = _slug(name)
    default_first = name
    default_last = "User"
    default_email = f"{_email_local(slug_name)}@localhost.com"

    create_agent = False
    if not restrict_user:
        create_agent = _prompt_yes("Create a new Agent for this webservice?", True)
        if create_agent:
            restrict_user = typer.prompt("Agent login", default=f"{slug_name}_ws".lower())
            first_name = typer.prompt("First name", default=default_first)
            last_name = typer.prompt("Last name", default=default_last)
            email = typer.prompt("Email", default=default_email)
        else:
            restrict_user = typer.prompt("Existing agent login to use", default="root@localhost")
    else:
        if not first_name:
            first_name = default_first
        if not last_name:
            last_name = default_last
        if not email:
            email = default_email

    enabled_ops: dict[str, None] = {OPERATIONS[o]: None for o in ops_clean}
    generator = WebServiceGenerator()
    yaml_content = generator.generate_yaml(
        webservice_name=name,
        enabled_operations=enabled_ops,
        restricted_user=restrict_user,
        framework_version=version,
    )

    target = out or Path(f"{slug_name}.yml")
    _write_file(target, yaml_content, force)

    typer.echo("Command to add webservice:")
    typer.echo(f"otobo.Console.pl Admin::WebService::Add --Name {name} --Config {target}")

    created_password = None
    if create_agent:
        created_password = _generate_password()
        typer.echo("Command to create agent:")
        typer.echo(
            f"otobo.Console.pl Admin::User::Add --UserFirstname \"{first_name}\" --UserLastname \"{last_name}\" "
            f"--UserLogin \"{restrict_user}\" --UserPassword \"{created_password}\" --UserEmail \"{email}\""
        )

    make_gq = _prompt_yes("Create a new Group and Queue for testing?", True)
    group_name = None
    queue_name = None
    if make_gq:
        group_name = typer.prompt("Group name", default=f"{slug_name}-group")
        queue_name = typer.prompt("Queue name", default=f"{slug_name}::Test")
        typer.echo("Commands to create group and queue:")
        typer.echo(f"otobo.Console.pl Admin::Group::Add --Name \"{group_name}\" --Valid 1")
        typer.echo(f"otobo.Console.pl Admin::Queue::Add --Name \"{queue_name}\" --Group \"{group_name}\" --Valid 1")
    else:
        group_name = typer.prompt("Existing group name", default="users")
        queue_name = typer.prompt("Existing queue name", default="Raw")

    grant_rights = _prompt_yes("Grant agent rights on the group (ro,note,create,move_into)?", True)
    if grant_rights:
        typer.echo("Command to link agent to group with permissions:")
        typer.echo(
            f"otobo.Console.pl Admin::Group::UserLink --group-name \"{group_name}\" --user-name \"{restrict_user}\" --permission \"ro,move_into,create,note\""
        )

    if write_env:
        lines = [f"OTOBO_SERVER_URL={base_url}", f"OTOBO_WEBSERVICE_NAME={name}", f"OTOBO_QUEUE={queue_name}"]
        lines.append(f"OTOBO_USERNAME={restrict_user}")
        _write_file(env_file, "\n".join(lines) + "\n", force)

    if not run_test:
        return

    op_urls = {k: f"{base_url.rstrip('/')}/Webservice/{name}/{v}" for k, v in OP_PATHS.items() if k in enabled_ops}

    auth_login = restrict_user
    auth_password = created_password or typer.prompt("Password for the agent to authenticate HTTP calls",
                                                     hide_input=True)

    created_ticket_number: Optional[str] = None
    created_ticket_id: Optional[int] = None

    if "TicketCreate" in enabled_ops:
        payload_create = {
            "UserLogin": auth_login,
            "Password": auth_password,
            "Ticket": {
                "Title": f"{name} setup test",
                "Queue": queue_name,
                "State": "open",
                "Priority": "3 normal",
                "CustomerUser": "test@example.com",
            },
            "Article": {
                "Subject": "Setup test",
                "Body": "Initial ticket via webservice",
                "MimeType": "text/plain",
                "Charset": "utf-8",
            },
        }
        res_c = _http_post(op_urls.get("TicketCreate", ""), payload_create)
        typer.echo(f"Create response: {json.dumps(res_c, ensure_ascii=False)}")
        created_ticket_number = res_c.get("TicketNumber")
        created_ticket_id = res_c.get("TicketID")

    if "TicketUpdate" in enabled_ops:
        if not created_ticket_id:
            if created_ticket_number and "TicketSearch" in enabled_ops:
                payload_search = {"UserLogin": auth_login, "Password": auth_password,
                                  "TicketNumber": created_ticket_number}
                res_s = _http_post(op_urls.get("TicketSearch", ""), payload_search)
                ids = res_s.get("TicketIDs") or []
                if isinstance(ids, list) and ids:
                    created_ticket_id = ids[0]
            if not created_ticket_id:
                num = typer.prompt("TicketNumber to update (no create op available or failed)",
                                   default=created_ticket_number or "")
                payload_search2 = {"UserLogin": auth_login, "Password": auth_password, "TicketNumber": num}
                res_s2 = _http_post(op_urls.get("TicketSearch", ""), payload_search2)
                ids2 = res_s2.get("TicketIDs") or []
                if isinstance(ids2, list) and ids2:
                    created_ticket_id = ids2[0]
        if created_ticket_id:
            payload_update = {
                "UserLogin": auth_login,
                "Password": auth_password,
                "TicketID": created_ticket_id,
                "Ticket": {"Priority": "4 high"},
                "Article": {"Subject": "Update", "Body": "Update via webservice"},
            }
            res_u = _http_post(op_urls.get("TicketUpdate", ""), payload_update)
            typer.echo(f"Update response: {json.dumps(res_u, ensure_ascii=False)}")

    tn_for_get = created_ticket_number
    if not tn_for_get:
        tn_for_get = typer.prompt("TicketNumber to fetch", default=created_ticket_number or "")
    if tn_for_get and "TicketSearch" in enabled_ops:
        res_s3 = _http_post(op_urls.get("TicketSearch", ""),
                            {"UserLogin": auth_login, "Password": auth_password, "TicketNumber": tn_for_get})
        typer.echo(f"Search response: {json.dumps(res_s3, ensure_ascii=False)}")
        ids3 = res_s3.get("TicketIDs") or []
        tid = ids3[0] if isinstance(ids3, list) and ids3 else None
        if tid and "TicketGet" in enabled_ops:
            res_g = _http_post(op_urls.get("TicketGet", ""),
                               {"UserLogin": auth_login, "Password": auth_password, "TicketID": tid})
            typer.echo(f"Get response: {json.dumps(res_g, ensure_ascii=False)}")


if __name__ == "__main__":
    app()
