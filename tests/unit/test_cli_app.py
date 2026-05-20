from __future__ import annotations

from typing import Any

import pytest
import typer
from typer.testing import CliRunner

from otobo_znuny.cli.app import _resolve_operations, app
from otobo_znuny.cli.command_models import CmdResult
from otobo_znuny.domain_models.ticket_operation import TicketOperation
from otobo_znuny.models.base_models import GroupConfig, QueueConfig, UserModel

pytestmark = pytest.mark.unit


class RecordingConsole:
    def __init__(self) -> None:
        self.calls: dict[str, Any] = {}

    def add_user(self, user: UserModel, quiet=None, no_ansi=None) -> CmdResult:
        self.calls["add_user"] = user.model_dump()
        return CmdResult(code=0, out="ok")

    def add_group(self, group: GroupConfig, quiet=None, no_ansi=None) -> CmdResult:
        self.calls["add_group"] = group.model_dump()
        return CmdResult(code=0, out="ok")

    def link_user_to_group(
        self,
        user_name: str,
        group_name: str,
        permission: str,
        quiet=None,
        no_ansi=None,
    ) -> CmdResult:
        self.calls["link_user_to_group"] = {
            "user_name": user_name,
            "group_name": group_name,
            "permission": permission,
        }
        return CmdResult(code=0, out="ok")

    def add_queue(self, queue: QueueConfig, quiet=None, no_ansi=None) -> CmdResult:
        self.calls["add_queue"] = queue.model_dump()
        return CmdResult(code=0, out="ok")


class FailingConsole:
    def add_group(self, group: GroupConfig, quiet=None, no_ansi=None) -> CmdResult:
        return CmdResult(code=5, err="boom")


runner = CliRunner()


def test_cli_commands_success(monkeypatch):
    console = RecordingConsole()
    monkeypatch.setattr("otobo_znuny.cli.app._build_console", lambda: console)

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
        ["link-user-to-group", "testuser", "devops", "--permission", "rw"],
    )
    assert result_link.exit_code == 0
    assert "Linked user 'testuser' to group 'devops' with permission 'rw'." in result_link.stdout

    result_queue = runner.invoke(
        app,
        ["add-queue", "Support", "devops", "--comment", "Queue comment", "--system-address-id", "42"],
    )
    assert result_queue.exit_code == 0
    assert "Queue 'Support' created successfully." in result_queue.stdout


def test_cli_command_failure(monkeypatch):
    monkeypatch.setattr("otobo_znuny.cli.app._build_console", lambda: FailingConsole())
    result = runner.invoke(app, ["add-group", "devops"])
    assert result.exit_code == 5
    assert "boom" in result.stderr


def test_cli_requires_environment(monkeypatch):
    monkeypatch.setattr("otobo_znuny.cli.app._ENV_CACHE", None)
    monkeypatch.setattr("otobo_znuny.cli.app.detect_system", lambda: None)
    result = runner.invoke(app, ["add-group", "devops"])
    assert result.exit_code == 2
    assert "Could not automatically detect an OTOBO/Znuny environment" in result.stderr


def test_resolve_operations_case_insensitive():
    operations = _resolve_operations(["create", "GeT"])
    assert operations == [TicketOperation.CREATE, TicketOperation.GET]


def test_resolve_operations_invalid():
    with pytest.raises(typer.BadParameter, match="Unknown operation 'unknown'"):
        _resolve_operations(["create", "unknown"])
