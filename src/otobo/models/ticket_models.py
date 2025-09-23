from typing import List

from pydantic import BaseModel


class WsTicketBase(BaseModel):
    Title: str | None = None
    Lock: str | None = None
    LockID: int | None = None
    QueueID: int | None = None
    Queue: str | None = None
    StateID: int | None = None
    State: str | None = None
    PriorityID: int | None = None
    Priority: str | None = None
    OwnerID: int | None = None
    Owner: str | None = None
    CustomerUser: str | None = None
    TicketID: int | None = None
    TicketNumber: str | None = None
    Type: str | None = None
    TypeID: int | None = None
    CustomerID: str | None = None
    CustomerUserID: str | None = None
    CreateBy: int | None = None
    ChangeBy: int | None = None
    Created: str | None = None
    Changed: str | None = None


class WsDynamicField(BaseModel):
    Name: str
    Value: str | None = None


class WsArticleDetail(BaseModel):
    ArticleID: int | None = None
    ArticleNumber: int | None = None
    From: str | None = None
    Subject: str | None = None
    Body: str | None = None
    ContentType: str | None = None
    CreateTime: str | None = None
    ChangeTime: str | None = None
    To: str | None = None
    MessageID: str | None = None
    ChangeBy: int | None = None
    CreateBy: int | None = None


class WsTicketOutput(WsTicketBase):
    Article: List[WsArticleDetail] | WsArticleDetail | None = None
    DynamicField: List[WsDynamicField] | None = None

    def get_articles(self) -> List[WsArticleDetail]:
        if self.Article is None:
            return []
        if isinstance(self.Article, list):
            return self.Article
        return [self.Article]
