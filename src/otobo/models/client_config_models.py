import enum
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from otobo.models.request_models import AuthData


class TicketOperation(Enum):
    """
    Enumeration of supported ticket operations in the OTOBO Webservice API.
    Each member stores both the OTOBO short name and the Type string.
    """
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
        """Return the OTOBO 'Type' string, e.g. 'Ticket::TicketCreate'."""
        return self.operation_type


class OTOBOClientConfig(BaseModel):
    """
    Configuration model for initializing an OTOBOClient.

    Attributes:
        base_url (str):
            The root URL of the OTOBO installation, e.g.
            `https://server/otobo/nph-genericinterface.pl`.
        service (str):
            The name of the generic interface connector configured in OTOBO.
        auth (AuthData):
            Authentication credentials or tokens required by the Webservice.
        operations (Dict[TicketOperation, str]):
            Mapping from TicketOperation enum members to the corresponding
            endpoint names as configured in OTOBO, for example:
            `{ TicketOperation.CREATE: "ticket-create", ... }`.
    """
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


