from typing import Union, List, Optional

from pydantic import BaseModel

from .ticket_models import TicketDetailOutput


class TicketCreateResponse(BaseModel):
    """
    Response model for ticket creation operation.

    Attributes:
        TicketID (Union[int, str]): The unique identifier of the ticket in OTOBO.
    """
    TicketID: Union[int, str]


class TicketGetResponse(BaseModel):
    """
    Simplified response model for a single ticket retrieval.

    Attributes:
        Ticket (TicketDetailOutput): Details of the fetched ticket.
    """
    Ticket: list[TicketDetailOutput]



class TicketUpdateResponse(BaseModel):
    """
    Response model for ticket update operation.

    Attributes:
        TicketID (int): Identifier of the ticket that was updated.
        ArticleID (Optional[int]): Identifier of the article created during update, if any.
        Ticket (TicketDetailOutput): Detailed information of the updated ticket.
    """
    TicketID: int
    ArticleID: Optional[int] = None
    Ticket: Optional[TicketDetailOutput] = None


class TicketSearchResponse(BaseModel):
    """
    Response model for ticket search operation.

    Attributes:
        TicketID (List[int]): List of ticket IDs matching the search criteria.
    """
    TicketID: List[int]
