from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from otobo.models.request_models import AuthData


class TicketOperation(Enum):
    CREATE = ("TicketCreate", "Ticket::TicketCreate")
    SEARCH = ("TicketSearch", "Ticket::TicketSearch")
    GET = ("TicketGet", "Ticket::TicketGet")
    UPDATE = ("TicketUpdate", "Ticket::TicketUpdate")

    def __new__(cls, name: str, operation_type: str):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.operation_type = operation_type
        return obj

    @property
    def type(self) -> str:
        return self.operation_type


class OTOBOClientConfig(BaseModel):
    base_url: str = Field(
        ...,
        description="Base URL of the OTOBO installation, e.g. https://server/otobo/nph-genericinterface.pl"
    )
    service: str = Field(
        ...,
        description="Webservice connector name"
    )
    auth: AuthData
    operations: Dict[TicketOperation, str] = Field(
        ...,
        description=(
            "Mapping of operation keys to endpoint names, "
            "e.g. {TicketOperation.CREATE: 'ticket-create', ...}"
        )
    )


