from typing import Union, List, Optional

from pydantic import BaseModel

from .ticket_models import TicketDetailOutput, TicketCommon, ArticleDetail


class OTOBOTicketCreateResponse(BaseModel):
    """
    Response model for ticket creation operation.

    Attributes:
        TicketNumber (str): The newly created ticket's human-readable number.
        TicketID (Union[int, str]): The unique identifier of the ticket in OTOBO.
        Ticket (TicketDetailOutput): Detailed information of the created ticket.
        ArticleID (int): Identifier of the article associated with ticket creation.
    """
    TicketNumber: str
    TicketID: Union[int, str]
    Ticket: TicketDetailOutput
    ArticleID: int


class OTOBOTicketGetResponse(BaseModel):
    """
    Response model for ticket retrieval operation, returns a list of tickets.

    Attributes:
        Ticket (List[TicketDetailOutput]): List of matching ticket details.
    """
    Ticket: List[TicketDetailOutput]


class TicketGetResponse(BaseModel):
    """
    Simplified response model for a single ticket retrieval.

    Attributes:
        Ticket (TicketDetailOutput): Details of the fetched ticket.
    """
    Ticket: TicketDetailOutput


class OTOBOTicketHistoryEntry(TicketCommon):
    """
    History entry model for a single ticket history record.

    Attributes:
        HistoryType (str): Name of the history event type.
        HistoryTypeID (int): Identifier of the history event type.
        Name (str): Descriptive name for the history entry.
    """
    HistoryType: str
    HistoryTypeID: int
    Name: str


class TicketHistoryModel(BaseModel):
    """
    Model representing the history list for a specific ticket.

    Attributes:
        TicketID (int): Identifier of the ticket.
        History (List[OTOBOTicketHistoryEntry]): List of history entries.
    """
    TicketID: int
    History: List[OTOBOTicketHistoryEntry] = []


class OTOBOTicketHistoryResponse(BaseModel):
    """
    Response model for fetching ticket history operations.

    Attributes:
        TicketHistory (List[TicketHistoryModel]): List of ticket history models.
    """
    TicketHistory: List[TicketHistoryModel]


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
    Ticket: TicketDetailOutput


class TicketSearchResponse(BaseModel):
    """
    Response model for ticket search operation.

    Attributes:
        TicketID (List[int]): List of ticket IDs matching the search criteria.
    """
    TicketID: List[int]


class FullTicketSearchResponse(BaseModel):
    """
    Combined response model for full ticket search and retrieval.

    Attributes:
        Ticket (List[TicketDetailOutput]): List of detailed ticket objects.
    """
    Ticket: List[TicketDetailOutput] = []
