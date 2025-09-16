from typing import Optional, Union, List, Dict, Literal

from pydantic import BaseModel, Field, field_validator

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
    Ticket: TicketBase | None = None
    Article: ArticleDetail | list[ArticleDetail] | None = None
    DynamicField: list[DynamicFieldItem] | None = None

    @field_validator("Article", mode="before")
    @classmethod
    def _coerce_article(cls, value):
        if value is None:
            return None
        if isinstance(value, ArticleDetail):
            return value
        if isinstance(value, dict):
            return ArticleDetail.model_validate(value, strict=False)
        if isinstance(value, (list, tuple)):
            return [
                x if isinstance(x, ArticleDetail) else ArticleDetail.model_validate(x, strict=False)
                for x in value
            ]
        raise TypeError("Article must be ArticleDetail | dict | list | None")

class TicketUpdateRequest(TicketCreateRequest):
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
