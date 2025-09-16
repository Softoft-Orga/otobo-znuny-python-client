from typing import Union, List, Optional

from pydantic import BaseModel

from otobo.models.ticket_models import TicketDetailOutput
from otobo.util.otobo_errors import OTOBOError

class TicketResponse(BaseModel):
    Ticket: Optional[TicketDetailOutput] = None


class TicketGetResponse(BaseModel):
    Ticket: list[TicketDetailOutput]


class TicketSearchResponse(BaseModel):
    TicketID: List[int] | None = None
