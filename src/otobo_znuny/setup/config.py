from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from models import UserModel
from otobo_znuny.cli.command_models import Permission
from otobo_znuny_python_client import TicketOperation


class SetupConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    webservice_name: str
    webservice_description: str
    enabled_operations: list[TicketOperation]

    user_to_add: UserModel | None = None

    user_users_permissions: list[Permission] | None = Field(
        default_factory=lambda: ["ro", "move_into", "create", "owner", "priority", "rw"])

    _webservice_restricted_user: str | None = None
    _restrict_webservice: bool = True

    @property
    def webservice_restricted_user(self) -> str | None:
        if not self._restrict_webservice:
            return None

        return self._webservice_restricted_user or self.user_to_add.user_name
