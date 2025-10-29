from __future__ import annotations

from typing import Literal, Any

import yaml
from pydantic import BaseModel

from domain_models.ticket_operation import TicketOperation


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class RouteMappingConfig(BaseModel):
    Route: str
    RequestMethod: list[str]
    ParserBackend: Literal["JSON"] = "JSON"


class ProviderOperationConfig(BaseModel):
    Type: str
    Description: str
    IncludeTicketData: Literal["0", "1"]
    MappingInbound: dict[str, Any]
    MappingOutbound: dict[str, Any]


class OperationSpec(BaseModel):
    op: TicketOperation
    route: str
    description: str
    methods: list[str]
    include_ticket_data: Literal["0", "1"]
