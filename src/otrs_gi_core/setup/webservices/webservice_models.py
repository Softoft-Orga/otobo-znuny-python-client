from __future__ import annotations

from pydantic import BaseModel

from otrs_gi_core.domain_models.ticket_operation import TicketOperation


class OperationSpec(BaseModel):
    operation_name: str
    op: TicketOperation
    route: str
    description: str
    methods: list[str]
    include_ticket_data: str
