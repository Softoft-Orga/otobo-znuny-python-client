from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest
import typer
from typer.testing import CliRunner

import otobo_znuny_python_client.cli.app as cli_app
from otobo_znuny_python_client.cli.app import _resolve_operations, app
from otobo_znuny_python_client.cli.command_models import CmdResult
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation


pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _allow_permission_union(monkeypatch):
    monkeypatch.setitem(cli_app.link_user_to_group.__annotations__, "permission", str)


class RecordingConsole:
    def __init__(self) -> None:
        self.calls: Dict[str, Any] = {}

    def add_user(
        self,
        user_name: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        groups: Optional[List[str]]
    ) -> CmdResult:
        self.calls["add_user"] = {
            "user_name": user_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "groups": groups,
        }
        return CmdResult(ok=True, code=0, out="ok", err="")

    def add_group(self, group_name: str, comment: Optional[str]) -> CmdResult:
        self.calls["add_group"] = {
            "group_name": group_name,
            "comment": comment,
        }
        return CmdResult(ok=True, code=0, out="ok", err="")

    def link_user_to_group(
        self,
        user_name: str,
        group_name: str,
        permission: str,
    ) -> CmdResult:
        self.calls["link_user_to_group"] = {
            "user_name": user_name,
            "group_name": group_name,
            "permission": permission,
        }
        return CmdResult(ok=True, code=0, out="ok", err="")

    def add_queue(
        self,
        name: str,
        group: str,
        *,
        comment: Optional[str] = None,
        system_address_id: Optional[int] = None,
        system_address_name: Optional[str] = None,
        unlock_timeout: Optional[int] = None,
        first_response_time: Optional[int] = None,
        update_time: Optional[int] = None,
        solution_time: Optional[int] = None,
        calendar: Optional[int] = None,
    ) -> CmdResult:
        self.calls["add_queue"] = {
            "name": name,
            "group": group,
            "comment": comment,
            "system_address_id": system_address_id,
            "system_address_name": system_address_name,
            "unlock_timeout": unlock_timeout,
            "first_response_time": first_response_time,
            "update_time": update_time,
            "solution_time": solution_time,
            "calendar": calendar,
        }
        return CmdResult(ok=True, code=0, out="ok", err="")


class FailingConsole:
    def add_group(self, group_name: str, comment: Optional[str]) -> CmdResult:
        return CmdResult(ok=False, code=5, out="", err="boom")


runner = CliRunner()


def test_cli_commands_success(monkeypatch):
    console = RecordingConsole()
    monkeypatch.setattr("otobo_znuny_python_client.cli.app._build_console", lambda: console)

    result_user = runner.invoke(
        app,
        [
            "add-user",
            "testuser",
            "First",
            "Last",
            "test@example.com",
            "--password",
            "s3cret",
            "--group",
            "admins",
            "--group",
            "users",
        ],
    )
    assert result_user.exit_code == 0
    assert "User 'testuser' created successfully." in result_user.stdout
    assert console.calls["add_user"]["groups"] == ["admins", "users"]

    result_group = runner.invoke(app, ["add-group", "devops", "--comment", "Ops"])
    assert result_group.exit_code == 0
    assert "Group 'devops' created successfully." in result_group.stdout

    result_link = runner.invoke(
        app,
        [
            "link-user-to-group",
            "testuser",
            "devops",
            "--permission",
            "rw",
        ],
    )
    assert result_link.exit_code == 0
    assert "Linked user 'testuser' to group 'devops' with permission 'rw'." in result_link.stdout

    result_queue = runner.invoke(
        app,
        [
            "add-queue",
            "Support",
            "devops",
            "--comment",
            "Queue comment",
            "--system-address-id",
            "42",
        ],
    )
    assert result_queue.exit_code == 0
    assert "Queue 'Support' created successfully." in result_queue.stdout


def test_cli_command_failure(monkeypatch):
    monkeypatch.setattr("otobo_znuny_python_client.cli.app._build_console", lambda: FailingConsole())

    result = runner.invoke(app, ["add-group", "devops"])
    assert result.exit_code == 5
    assert "boom" in result.stderr


def test_cli_requires_environment(monkeypatch):
    monkeypatch.setattr("otobo_znuny_python_client.cli.app._ENV_CACHE", None)
    monkeypatch.setattr("otobo_znuny_python_client.cli.app.detect_environment", lambda: None)

    result = runner.invoke(app, ["add-group", "devops"])
    assert result.exit_code == 2
    assert "Could not automatically detect an OTOBO/Znuny environment" in result.stderr


def test_resolve_operations_case_insensitive():
    operations = _resolve_operations(["create", "GeT"])
    assert operations == [TicketOperation.CREATE, TicketOperation.GET]


def test_resolve_operations_invalid():
    with pytest.raises(typer.BadParameter, match="Unknown operation 'unknown'"):
        _resolve_operations(["create", "unknown"])
