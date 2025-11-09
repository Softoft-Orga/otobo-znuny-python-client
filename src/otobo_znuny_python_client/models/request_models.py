from typing import Literal

from pydantic import BaseModel, Field, SecretStr

from otobo_znuny_python_client.models.base_models import BooleanInteger
from otobo_znuny_python_client.models.ticket_models import WsArticle, WsDynamicField, WsTicketBase
from otobo_znuny_python_client.util.safe_base_model import SafeBaseModel


class WsAuthData(SafeBaseModel):
    UserLogin: str = Field(..., description="Agent login for authentication")
    Password: SecretStr = Field(..., description="Agent password for authentication")


class WsTicketSearchRequest(BaseModel):
    Limit: int = 10_000
    SearchLimit: int = 10_000
    TicketLastChangeTimeNewerDate: str | None = None  # All tickets updated newer than this date
    TicketLastChangeTimeOlderDate: str | None = None  # All tickets updated older than this date
    SearchInArchive: str = "AllTickets"


class WsTicketGetRequest(BaseModel):
    DynamicFields: BooleanInteger = 1
    Extended: BooleanInteger = 1
    AllArticles: BooleanInteger = 1
    ArticleSenderType: list[str] | None = None
    ArticleOrder: Literal["ASC", "DESC"] = "ASC"
    ArticleLimit: int = 5
    Attachments: BooleanInteger = 1
    GetAttachmentContents: BooleanInteger = 1
    HTMLBodyAsAttachment: BooleanInteger = 1


class WsTicketMutationRequest(BaseModel):
    Ticket: WsTicketBase | None = None
    Article: WsArticle | None = None
    DynamicField: list[WsDynamicField] | None = None


class WsTicketUpdateRequest(WsTicketMutationRequest):
    TicketID: int | None = None
    TicketNumber: str | None = None
