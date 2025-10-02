from pydantic import BaseModel

from otobo_znuny.models.ticket_models import WsTicketOutput


class WsTicketResponse(BaseModel):
    Ticket: WsTicketOutput | None = None


class WsTicketGetResponse(BaseModel):
    Ticket: list[WsTicketOutput]


class WsTicketSearchResponse(BaseModel):
    TicketID: list[int] | None = None
