from typing import Any, List, Union, Optional
from pydantic import BaseModel


class OTOBOTicketBase(BaseModel):
    Title: Optional[str] = None
    Lock: Optional[str] = None
    LockID: Optional[int] = None
    QueueID: Optional[int] = None
    Queue: Optional[str] = None
    StateID: Optional[int] = None
    State: Optional[str] = None
    PriorityID: Optional[int] = None
    Priority: Optional[str] = None
    OwnerID: Optional[int] = None
    Owner: Optional[str] = None
    CustomerUser: Optional[str] = None
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
    Type: Optional[str] = None
    TypeID: Optional[int] = None
    CustomerID: Optional[str] = None
    CustomerUserID: Optional[str] = None
    CreateBy: Optional[int] = None
    ChangeBy: Optional[int] = None
    Created: Optional[str] = None
    Changed: Optional[str] = None



class DynamicFieldItem(BaseModel):
    Name: str
    Value: Optional[Any] = None


class ArticleDetail(BaseModel):
    ArticleID: Optional[int] = None
    ArticleNumber: Optional[int] = None
    From: Optional[str] = None
    Subject: Optional[str] = None
    Body: Optional[str] = None
    ContentType: Optional[str] = None
    CreateTime: Optional[str] = None
    ChangeTime: Optional[str] = None
    To: Optional[str] = None
    MessageID: Optional[str] = None
    ChangeBy: Optional[int] = None
    CreateBy: Optional[int] = None


class TicketDetailOutput(OTOBOTicketBase):
    Article: List[ArticleDetail] | ArticleDetail | None = None
    DynamicField: List[DynamicFieldItem] | None = None


