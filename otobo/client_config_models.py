from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from models.request_models import AuthData


class TicketOperation(Enum):
    CREATE = "TicketCreate"
    SEARCH = "TicketSearch"
    GET = "TicketGet"
    UPDATE = "TicketUpdate"
    HISTORY_GET = "TicketHistoryGet"


class OTOBOClientConfig(BaseModel):
    base_url: str = Field(...,
                          description="Base URL of the OTOBO installation, e.g. https://server/otobo/nph-genericinterface.pl")
    service: str = Field(..., description="Webservice connector name")
    auth: AuthData
    operations: Dict[TicketOperation, str] = Field(...,
                                                   description="Mapping of operation keys to endpoint names, e.g. {'TicketCreate': 'ticket-create', ...}")


