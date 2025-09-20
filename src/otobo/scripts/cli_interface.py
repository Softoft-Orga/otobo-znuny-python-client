from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Permission = Literal["ro", "move_into", "create", "owner", "priority", "rw"]


@dataclass
class CmdResult:
    ok: bool
    code: int
    out: str
    err: str


class Args:
    def __init__(self):
        self._parts: list[str] = []

    def opt(self, name: str, value: str | int | Path | None = None) -> Args:
        if value is None:
            self._parts.append(name)
        else:
            self._parts.extend([name, str(value)])
        return self

    def flag(self, name: str, enabled: bool = True) -> Args:
        if enabled:
            self._parts.append(name)
        return self

    def repeat(self, name: str, values: list[str | int | Path]) -> Args:
        for v in values:
            self._parts.extend([name, str(v)])
        return self

    def to_list(self) -> list[str]:
        return list(self._parts)


class CommandRunner:
    def __init__(self, prefix: list[str], executable: Path):
        self.prefix = prefix
        self.executable = executable

    @classmethod
    def from_docker(cls, container: str = "otobo-web-1",
                    console_path: Path = Path("./bin/otobo.Console.pl")) -> CommandRunner:
        return cls(["docker", "exec", container], console_path)

    @classmethod
    def from_local(cls, console_path: Path = Path("/opt/otobo/bin/otobo.Console.pl")) -> CommandRunner:
        return cls([], console_path)

    def run(self, operation: str, args: list[str]) -> CmdResult:
        cmd = [*self.prefix, self.executable, operation, *args]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return CmdResult(proc.returncode == 0, proc.returncode, proc.stdout.strip(), proc.stderr.strip())


class OtoboConsole:
    def __init__(self, runner: CommandRunner, no_ansi_default: bool = True, quiet_default: bool = False):
        self.runner = runner
        self.no_ansi_default = no_ansi_default
        self.quiet_default = quiet_default

    def _common(self, quiet: bool | None, no_ansi: bool | None) -> Args:
        a = Args()
        a.flag("--no-ansi", enabled=self.no_ansi_default if no_ansi is None else no_ansi)
        a.flag("--quiet", enabled=self.quiet_default if quiet is None else quiet)
        return a

    def add_user(
            self,
            user_name: str,
            first_name: str,
            last_name: str,
            email_address: str,
            password: str | None = None,
            groups: list[str] | None = None,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        a = self._common(quiet, no_ansi)
        a.opt("--user-name", user_name)
        a.opt("--first-name", first_name)
        a.opt("--last-name", last_name)
        a.opt("--email-address", email_address)
        if password:
            a.opt("--password", password)
        if groups:
            a.repeat("--group", groups)
        return self.runner.run("Admin::User::Add", a.to_list())

    def add_group(self, name: str, comment: str | None = None, quiet: bool | None = None,
                  no_ansi: bool | None = None) -> CmdResult:
        a = self._common(quiet, no_ansi)
        a.opt("--name", name)
        if comment:
            a.opt("--comment", comment)
        return self.runner.run("Admin::Group::Add", a.to_list())

    def link_user_to_group(
            self,
            user_name: str,
            group_name: str,
            permission: Permission | str,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        a = self._common(quiet, no_ansi)
        a.opt("--user-name", user_name)
        a.opt("--group-name", group_name)
        a.opt("--permission", permission)
        return self.runner.run("Admin::Group::UserLink", a.to_list())

    def add_queue(
            self,
            name: str,
            group: str,
            system_address_id: int | None = None,
            system_address_name: str | None = None,
            comment: str | None = None,
            unlock_timeout: int | None = None,
            first_response_time: int | None = None,
            update_time: int | None = None,
            solution_time: int | None = None,
            calendar: int | None = None,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        a = self._common(quiet, no_ansi)
        a.opt("--name", name)
        a.opt("--group", group)
        if system_address_id is not None:
            a.opt("--system-address-id", system_address_id)
        if system_address_name:
            a.opt("--system-address-name", system_address_name)
        if comment:
            a.opt("--comment", comment)
        if unlock_timeout is not None:
            a.opt("--unlock-timeout", unlock_timeout)
        if first_response_time is not None:
            a.opt("--first-response-time", first_response_time)
        if update_time is not None:
            a.opt("--update-time", update_time)
        if solution_time is not None:
            a.opt("--solution-time", solution_time)
        if calendar is not None:
            a.opt("--calendar", calendar)
        return self.runner.run("Admin::Queue::Add", a.to_list())

    def add_webservice(self, name: str, source_path: str | Path, quiet: bool | None = None,
                       no_ansi: bool | None = None) -> CmdResult:
        a = self._common(quiet, no_ansi)
        a.opt("--name", name)
        a.opt("--source-path", Path(source_path))
        return self.runner.run("Admin::WebService::Add", a.to_list())
