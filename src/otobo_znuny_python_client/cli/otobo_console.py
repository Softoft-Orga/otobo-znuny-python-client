from __future__ import annotations

from pathlib import Path

from .command_models import ArgsBuilder, CmdResult, OTOBO_COMMANDS, Permission
from .otobo_command_runner import OtoboCommandRunner


class OtoboConsole:
    def __init__(self, runner: OtoboCommandRunner, no_ansi_default: bool = True, quiet_default: bool = False):
        self.runner = runner
        self.no_ansi_default = no_ansi_default
        self.quiet_default = quiet_default

    def _common(self, quiet: bool | None, no_ansi: bool | None) -> ArgsBuilder:
        return (ArgsBuilder()
                .flag("--no-ansi", enabled=self.no_ansi_default if no_ansi is None else no_ansi)
                .flag("--quiet", enabled=self.quiet_default if quiet is None else quiet)
                )

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
        return self.runner.run(
            OTOBO_COMMANDS["AddUser"],
            (self._common(quiet, no_ansi)
             .opt("--user-name", user_name)
             .opt("--first-name", first_name)
             .opt("--last-name", last_name)
             .opt("--email-address", email_address)
             .opt_if("--password", password)
             .repeat_if("--group", groups)
             ).to_list(),
        )

    def add_group(self, name: str,
                  comment: str | None = None,
                  quiet: bool | None = None,
                  no_ansi: bool | None = None) -> CmdResult:
        return self.runner.run(
            OTOBO_COMMANDS["AddGroup"], (
                self._common(quiet, no_ansi)
                .opt("--name", name)
                .opt_if("--comment", comment)
            ).to_list(),
        )

    def link_user_to_group(
            self,
            user_name: str,
            group_name: str,
            permission: Permission | str,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        return self.runner.run(
            OTOBO_COMMANDS["LinkUserToGroup"],
            (self._common(quiet, no_ansi)
             .opt("--user-name", user_name)
             .opt("--group-name", group_name)
             .opt("--permission", permission)
             ).to_list(),
        )

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
        return self.runner.run(
            OTOBO_COMMANDS["AddQueue"],
            (self._common(quiet, no_ansi)
             .opt("--name", name)
             .opt("--group", group)
             .opt_if("--system-address-id", system_address_id)
             .opt_if("--system-address-name", system_address_name)
             .opt_if("--comment", comment)
             .opt_if("--unlock-timeout", unlock_timeout)
             .opt_if("--first-response-time", first_response_time)
             .opt_if("--update-time", update_time)
             .opt_if("--solution-time", solution_time)
             .opt_if("--calendar", calendar)
             ).to_list(),
        )

    def add_webservice(
            self,
            name: str,
            source_path: str | Path,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        return self.runner.run(
            OTOBO_COMMANDS["AddWebservice"],
            (self._common(quiet, no_ansi)
             .opt("--name", name)
             .opt("--source-path", Path(source_path))
             ).to_list(),
        )
