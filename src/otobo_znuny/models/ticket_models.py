from typing import List, Optional, Union

from pydantic import BaseModel


class WsTicketBase(BaseModel):
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


class WsDynamicField(BaseModel):
    Name: str
    Value: Optional[str] = None


class WsArticleDetail(BaseModel):
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


class WsTicketOutput(WsTicketBase):
    Article: Union[List[WsArticleDetail], WsArticleDetail, None] = None
    DynamicField: Optional[List[WsDynamicField]] = None

    def get_articles(self) -> List[WsArticleDetail]:
        if self.Article is None:
            return []
        if isinstance(self.Article, list):
            return self.Article
        return [self.Article]
