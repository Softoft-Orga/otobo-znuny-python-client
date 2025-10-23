from typing import Literal

from pydantic import BaseModel, Field, SecretStr, model_serializer

from otobo_znuny_python_client.models.base_models import BooleanInteger
from otobo_znuny_python_client.models.ticket_models import WsArticleDetail, WsDynamicField, WsTicketBase
from otobo_znuny_python_client.util.safe_base_model import SafeBaseModel


class WsDynamicFieldFilter(BaseModel):
    Empty: BooleanInteger = 1
    Equals: str | None = None
    Like: str | None = None
    GreaterThan: str | None = None
    GreaterThanEquals: str | None = None
    SmallerThan: str | None = None
    SmallerThanEquals: str | None = None


class WsAuthData(SafeBaseModel):
    UserLogin: str = Field(..., description="Agent login for authentication")
    Password: SecretStr = Field(..., description="Agent password for authentication")


class WsTicketSearchRequest(BaseModel):
    TicketNumber: str | list[str] | None = None
    Title: str | list[str] | None = None
    Locks: list[str] | None = None
    LockIDs: list[int] | None = None
    Queues: list[str] | None = None
    QueueIDs: list[int] | None = None
    UseSubQueues: bool | None = False
    Types: list[str] | None = None
    TypeIDs: list[int] | None = None
    States: list[str] | None = None
    StateIDs: list[int] | None = None
    Priorities: list[str] | None = None
    PriorityIDs: list[int] | None = None
    Limit: int = 0
    SearchLimit: int = 0
    DynamicFields: dict[str, WsDynamicFieldFilter] = {}

    @model_serializer(mode="wrap")
    def _serialize(self, serializer):
        data = serializer(self)
        dyn = data.pop("DynamicFields", None)
        if dyn:
            for k, v in dyn.items():
                data[f"DynamicField_{k}"] = v
        return data


class WsTicketGetRequest(BaseModel):
    TicketID: int | None = None
    DynamicFields: BooleanInteger = 1
    Extended: BooleanInteger = 1
    AllArticles: BooleanInteger = 1
    ArticleSenderType: list[str] | None = None
    ArticleOrder: Literal["ASC", "DESC"] = "ASC"
    ArticleLimit: int = 5
    Attachments: BooleanInteger = 0
    GetAttachmentContents: BooleanInteger = 1
    HTMLBodyAsAttachment: BooleanInteger = 1


class WsTicketMutationRequest(BaseModel):
    Ticket: WsTicketBase | None = None
    Article: WsArticleDetail | None = None
    DynamicField: list[WsDynamicField] | None = None


class WsTicketUpdateRequest(WsTicketMutationRequest):
    TicketID: int | None = None
    TicketNumber: str | None = None
