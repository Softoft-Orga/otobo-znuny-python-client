from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from zxcvbn import zxcvbn

from .command_models import ArgsBuilder, CmdResult, OTOBO_COMMANDS, Permission, PasswordToWeak
from .otobo_command_runner import OtoboCommandRunner

if TYPE_CHECKING:
    from ..models.base_models import UserModel, GroupConfig, QueueConfig
logger = logging.getLogger(__name__)

PERMISSION_MAP = {
    "owner": "owner",
    "move": "move_into",
    "priority": "priority",
    "create": "create",
    "read": "ro",
    "full": "rw",
}


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

    def is_strong_password(self, password: str) -> bool:
        password_strength = zxcvbn(password)
        return password_strength['guesses_log10'] >= 9

    def add_user(
            self,
            user: UserModel,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        logger.info(f"Adding user: {user.user_name} ({user.email})")
        if not self.is_strong_password(user.password):
            logger.warning(
                f"The provided password for user '{user.user_name}' is weak. ")
            return PasswordToWeak()
        return self.runner.run(
            OTOBO_COMMANDS["AddUser"],
            (self._common(quiet, no_ansi)
             .opt("--user-name", user.user_name)
             .opt("--first-name", user.first_name)
             .opt("--last-name", user.last_name)
             .opt("--email-address", user.email)
             .opt_if("--password", user.password)
             .repeat_if("--group", user.groups)
             ).to_list(),
        )

    def add_group(
            self,
            group: GroupConfig,
            quiet: bool | None = None,
            no_ansi: bool | None = None
    ) -> CmdResult:
        logger.info(f"Adding group: {group.name}")
        return self.runner.run(
            OTOBO_COMMANDS["AddGroup"], (
                self._common(quiet, no_ansi)
                .opt("--name", group.name)
                .opt_if("--comment", group.comment)
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
        logger.info(f"Linking user '{user_name}' to group '{group_name}' with permission '{permission}'")
        return self.runner.run(
            OTOBO_COMMANDS["LinkUserToGroup"],
            (self._common(quiet, no_ansi)
             .opt("--user-name", user_name)
             .opt("--group-name", group_name)
             .opt("--permission", permission)
             ).to_list(),
        )

    def link_user_to_group_with_permissions(
            self,
            user_name: str,
            group_name: str,
            permissions: list[Permission],
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        """
        Link a user to a group with multiple permissions.

        Args:
            user_name: Username to link
            group_name: Group name to link to
            permissions: List of permissions (can use friendly names like 'read', 'full', etc.)
            quiet: Suppress output
            no_ansi: Disable ANSI colors

        Returns:
            Dictionary mapping permission to CmdResult
        """
        logger.info(f"Linking user '{user_name}' to group '{group_name}' with permissions: {permissions}")
        results = []
        for permission in permissions:
            mapped_permission = PERMISSION_MAP.get(permission, permission)
            result = self.link_user_to_group(user_name, group_name, mapped_permission, quiet, no_ansi)
            results.append(result)
        return CmdResult.union(results)

    def add_queue(
            self,
            queue: QueueConfig,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        logger.info(f"Adding queue: {queue.name} (group: {queue.group})")

        return self.runner.run(
            OTOBO_COMMANDS["AddQueue"],
            (self._common(quiet, no_ansi)
             .opt("--name", queue.name)
             .opt("--group", queue.group)
             .opt_if("--system-address-id", queue.system_address_id)
             .opt_if("--system-address-name", queue.system_address_name)
             .opt_if("--comment", queue.comment)
             .opt_if("--unlock-timeout", queue.unlock_timeout)
             .opt_if("--first-response-time", queue.first_response_time)
             .opt_if("--update-time", queue.update_time)
             .opt_if("--solution-time", queue.solution_time)
             .opt_if("--calendar", queue.calendar)
             ).to_list(),
        )

    def add_webservice(
            self,
            name: str,
            source_path: str,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        logger.info(f"Adding webservice: {name} from {source_path}")
        return self.runner.run(
            OTOBO_COMMANDS["AddWebservice"],
            (self._common(quiet, no_ansi)
             .opt("--name", name)
             .opt("--source-path", source_path)
             ).to_list(),
        )

    def list_all_queues(
            self,
            quiet: bool | None = None,
            no_ansi: bool | None = None,
    ) -> CmdResult:
        """
        List all queues in the OTOBO/Znuny system.

        Returns:
            CmdResult with queue list in the output
        """
        logger.info("Listing all queues")
        return self.runner.run(
            OTOBO_COMMANDS["ListQueues"],
            self._common(quiet, no_ansi).to_list(),
        )
