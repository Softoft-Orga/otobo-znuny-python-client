from typing import Optional
from pydantic import BaseModel

from otobo_znuny.models.ticket_models import WsTicketOutput


class WsTicketResponse(BaseModel):
    Ticket: Optional[WsTicketOutput] = None


class WsTicketGetResponse(BaseModel):
    Ticket: list[WsTicketOutput] = []


class WsTicketSearchResponse(BaseModel):
    TicketID: Optional[list[int]] = None
