from typing import Optional, Union, List, Literal

from pydantic import BaseModel, Field, model_serializer, SecretStr

from otobo_znuny.models.base_models import BooleanInteger
from otobo_znuny.util.safe_base_model import SafeBaseModel
from otobo_znuny.models.ticket_models import WsDynamicField, WsTicketBase, WsArticleDetail


class WsDynamicFieldFilter(BaseModel):
    Empty: BooleanInteger = 1
    Equals: Optional[str] = None
    Like: Optional[str] = None
    GreaterThan: Optional[str] = None
    GreaterThanEquals: Optional[str] = None
    SmallerThan: Optional[str] = None
    SmallerThanEquals: Optional[str] = None


class WsAuthData(SafeBaseModel):
    UserLogin: str = Field(..., description="Agent login for authentication")
    Password: SecretStr = Field(..., description="Agent password for authentication")


class WsTicketSearchRequest(BaseModel):
    TicketNumber: Optional[Union[str, List[str]]] = None
    Title: Optional[Union[str, List[str]]] = None
    Locks: Optional[List[str]] = None
    LockIDs: Optional[List[int]] = None
    Queues: Optional[List[str]] = None
    QueueIDs: Optional[List[int]] = None
    UseSubQueues: Optional[bool] = False
    Types: Optional[List[str]] = None
    TypeIDs: Optional[List[int]] = None
    States: Optional[List[str]] = None
    StateIDs: Optional[List[int]] = None
    Priorities: Optional[List[str]] = None
    PriorityIDs: Optional[List[int]] = None
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
    TicketID: Optional[int] = None
    DynamicFields: BooleanInteger = 1
    Extended: BooleanInteger = 1
    AllArticles: BooleanInteger = 1
    ArticleSenderType: Optional[List[str]] = None
    ArticleOrder: Literal["ASC", "DESC"] = 'ASC'
    ArticleLimit: int = 5
    Attachments: BooleanInteger = 0
    GetAttachmentContents: BooleanInteger = 1
    HTMLBodyAsAttachment: BooleanInteger = 1


class WsTicketMutationRequest(BaseModel):
    Ticket: Optional[WsTicketBase] = None
    Article: Optional[WsArticleDetail] = None
    DynamicField: Optional[list[WsDynamicField]] = None


class WsTicketUpdateRequest(WsTicketMutationRequest):
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
