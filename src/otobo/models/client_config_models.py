import enum
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from .request_models import AuthData


class TicketOperation(Enum):
    """
    Enumeration of supported ticket operations in the OTOBO Webservice API.

    Members:
        CREATE:       Create a new ticket (TicketCreate).
        SEARCH:       Search for existing tickets (TicketSearch).
        GET:          Retrieve a specific ticket by ID (TicketGet).
        UPDATE:       Update fields of an existing ticket (TicketUpdate).
        HISTORY_GET:  Fetch the history entries for a ticket (TicketHistoryGet).
    """
    CREATE = "TicketCreate"
    SEARCH = "TicketSearch"
    GET = "TicketGet"
    UPDATE = "TicketUpdate"


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
