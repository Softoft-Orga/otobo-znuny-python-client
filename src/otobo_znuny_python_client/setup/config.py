from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from domain_models.ticket_operation import TicketOperation


class SetupConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    webservice_name: str
    webservice_description: str
    enabled_operations: list[TicketOperation]

    group_name: str
    group_comment: str

    user_name: str
    user_first_name: str
    user_last_name: str
    user_email: str
    user_password: str
    user_permissions: list[str]

    queue_name: str
    queue_comment: str
