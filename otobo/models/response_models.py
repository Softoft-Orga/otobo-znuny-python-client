from typing import Union, List, Optional

from pydantic import BaseModel

from models.ticket_models import TicketDetailOutput, TicketCommon, ArticleDetail


class OTOBOTicketCreateResponse(BaseModel):
    TicketNumber: str
    TicketID: Union[int, str]
    Ticket: TicketDetailOutput
    ArticleID: int


# --- Models for Ticket Get Response ---
class OTOBOTicketGetResponse(BaseModel):
    Ticket: List[TicketDetailOutput]


class TicketGetResponse(BaseModel):
    Ticket: TicketDetailOutput


# --- Models for Ticket TicketHistoryModel Response ---
class OTOBOTicketHistoryEntry(TicketCommon):
    HistoryType: str
    HistoryTypeID: int
    Name: str



class TicketHistoryModel(BaseModel):
    TicketID: int
    History: List[OTOBOTicketHistoryEntry] = []


class OTOBOTicketHistoryResponse(BaseModel):
    TicketHistory: List[TicketHistoryModel]


class TicketUpdateResponse(BaseModel):
    TicketID: int
    ArticleID: Optional[int] = None
    Ticket: TicketDetailOutput


class TicketSearchResponse(BaseModel):
    TicketID: List[int]


class FullTicketSearchResponse(BaseModel):
    Ticket: List[TicketDetailOutput] = []