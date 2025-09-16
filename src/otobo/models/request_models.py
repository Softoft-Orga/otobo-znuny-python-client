from typing import Optional, Union, List, Dict, Literal

from pydantic import BaseModel, Field

from otobo.models.ticket_models import TicketBase, ArticleDetail, DynamicFieldItem


class AuthData(BaseModel):
    UserLogin: str = Field(..., description="Agent login for authentication")
    Password: str = Field(..., description="Agent password for authentication")


class TicketSearchRequest(BaseModel):
    TicketNumber: Optional[Union[str, List[str]]] = None
    Title: Optional[Union[str, List[str]]] = None
    Queues: Optional[List[str]] = None
    QueueIDs: Optional[List[int]] = None
    UseSubQueues: Optional[bool] = False
    Types: Optional[List[str]] = None
    TypeIDs: Optional[List[int]] = None
    States: Optional[List[str]] = None
    StateIDs: Optional[List[int]] = None
    Priorities: Optional[List[str]] = None
    PriorityIDs: Optional[List[int]] = None




class TicketGetRequest(BaseModel):
    TicketID: Optional[int] = None
    DynamicFields: int = 1
    Extended: int = 1
    AllArticles: int = 1
    ArticleSenderType: Optional[List[str]] = None
    ArticleOrder: Literal["ASC", "DESC"] = 'ASC'
    ArticleLimit: int = 20
    Attachments: int = 0
    GetAttachmentContents: int = 1
    HTMLBodyAsAttachment: int = 1


class TicketCreateRequest(BaseModel):
    Ticket: Optional[TicketBase] = None
    Article: Optional[Union[ArticleDetail, List[ArticleDetail]]] = None
    DynamicField: Optional[List[DynamicFieldItem]] = None


class TicketUpdateRequest(TicketCreateRequest):
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
