import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from otobo.scripts.cli_interface import OtoboConsole, CmdResult, CommandRunner


class RunSpy:
    def __init__(self):
        self.calls = []
        self.returncode = 0
        self.stdout = "ok"
        self.stderr = ""

    def __call__(self, cmd, capture_output=True, text=True):
        self.calls.append({"cmd": cmd, "capture_output": capture_output, "text": text})
        return SimpleNamespace(returncode=self.returncode, stdout=self.stdout, stderr=self.stderr)


@pytest.fixture
def spy(monkeypatch):
    s = RunSpy()
    monkeypatch.setattr(subprocess, "run", s)
    return s


def test_add_user_with_groups_docker(spy):
    runner = CommandRunner.from_docker(container="otobo-web-1", console_path="./bin/otobo.Console.pl")
    console = OtoboConsole(runner)
    res = console.add_user(
        user_name="tobi",
        first_name="Tobias",
        last_name="Bueck",
        email_address="tobi@example.com",
        password="secret",
        groups=["users", "admins"],
        quiet=False,
        no_ansi=True,
    )
    assert isinstance(res, CmdResult)
    assert res.ok is True
    expected = [
        "docker",
        "exec",
        "otobo-web-1",
        "./bin/otobo.Console.pl",
        "Admin::User::Add",
        "--no-ansi",
        "--user-name",
        "tobi",
        "--first-name",
        "Tobias",
        "--last-name",
        "Bueck",
        "--email-address",
        "tobi@example.com",
        "--password",
        "secret",
        "--group",
        "users",
        "--group",
        "admins",
    ]
    assert spy.calls[-1]["cmd"] == expected


def test_add_group_local_with_flags(spy):
    runner = CommandRunner.from_local(console_path="/opt/otobo/bin/otobo.Console.pl")
    console = OtoboConsole(runner)
    res = console.add_group(name="Support", comment="All agents", quiet=True, no_ansi=False)
    assert res.ok is True
    expected = [
        "/opt/otobo/bin/otobo.Console.pl",
        "Admin::Group::Add",
        "--quiet",
        "--name",
        "Support",
        "--comment",
        "All agents",
    ]
    assert spy.calls[-1]["cmd"] == expected


def test_link_user_to_group_permission(spy):
    runner = CommandRunner.from_local()
    console = OtoboConsole(runner)
    res = console.link_user_to_group(user_name="tobi", group_name="Support", permission="rw")
    assert res.ok is True
    expected = [
        "/opt/otobo/bin/otobo.Console.pl",
        "Admin::Group::UserLink",
        "--no-ansi",
        "--user-name",
        "tobi",
        "--group-name",
        "Support",
        "--permission",
        "rw",
    ]
    assert spy.calls[-1]["cmd"] == expected


def test_add_queue_all_options(spy):
    runner = CommandRunner.from_docker(container="c1", console_path="/bin/console.pl")
    console = OtoboConsole(runner)
    res = console.add_queue(
        name="Raw",
        group="users",
        system_address_id=2,
        system_address_name="help@acme.test",
        comment="Queue",
        unlock_timeout=10,
        first_response_time=30,
        update_time=60,
        solution_time=120,
        calendar=1,
    )
    assert res.ok is True
    expected = [
        "docker",
        "exec",
        "c1",
        "/bin/console.pl",
        "Admin::Queue::Add",
        "--no-ansi",
        "--name",
        "Raw",
        "--group",
        "users",
        "--system-address-id",
        "2",
        "--system-address-name",
        "help@acme.test",
        "--comment",
        "Queue",
        "--unlock-timeout",
        "10",
        "--first-response-time",
        "30",
        "--update-time",
        "60",
        "--solution-time",
        "120",
        "--calendar",
        "1",
    ]
    assert spy.calls[-1]["cmd"] == expected


def test_add_webservice_with_path_object_and_nonzero_rc(spy):
    spy.returncode = 1
    spy.stdout = ""
    spy.stderr = "error"
    runner = CommandRunner.from_local()
    console = OtoboConsole(runner)
    res = console.add_webservice(name="WS", source_path=Path("/tmp/ws.yml"))
    assert isinstance(res, CmdResult)
    assert res.ok is False
    assert res.code == 1
    assert res.out == ""
    assert res.err == "error"
    expected = [
        "/opt/otobo/bin/otobo.Console.pl",
        "Admin::WebService::Add",
        "--no-ansi",
        "--name",
        "WS",
        "--source-path",
        "/tmp/ws.yml",
    ]
    assert spy.calls[-1]["cmd"] == expected


def test_common_flags_overrides(spy):
    runner = CommandRunner.from_local()
    console = OtoboConsole(runner, no_ansi_default=False, quiet_default=True)
    res = console.add_group(name="A", quiet=None, no_ansi=None)
    assert res.ok is True
    expected1 = [
        "/opt/otobo/bin/otobo.Console.pl",
        "Admin::Group::Add",
        "--quiet",
        "--name",
        "A",
    ]
    assert spy.calls[-1]["cmd"] == expected1
    res2 = console.add_group(name="B", quiet=False, no_ansi=True)
    assert res2.ok is True
    expected2 = [
        "/opt/otobo/bin/otobo.Console.pl",
        "Admin::Group::Add",
        "--no-ansi",
        "--name",
        "B",
    ]
    assert spy.calls[-1]["cmd"] == expected2
