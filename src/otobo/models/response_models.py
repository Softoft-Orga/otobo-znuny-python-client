from typing import Union, List, Optional

from pydantic import BaseModel

from otobo.models.ticket_models import TicketDetailOutput
from otobo.util.otobo_errors import OTOBOError

class TicketResponse(BaseModel):
    Ticket: Optional[TicketDetailOutput] = None


class TicketGetResponse(BaseModel):
    """
    Simplified response model for a single ticket retrieval.

    Attributes:
        Ticket (TicketDetailOutput): Details of the fetched ticket.
    """
    Ticket: list[TicketDetailOutput]


class TicketSearchResponse(BaseModel):
    """
    Response model for ticket search operation.

    Attributes:
        TicketID (List[int]): List of ticket IDs matching the search criteria.
    """
    TicketID: List[int]
