from typing import Any, List, Union, Optional
from pydantic import BaseModel


class TicketBase(BaseModel):
    """
    Common fields for ticket creation and updates.

    Attributes:
        Title (Optional[str]): Subject or title of the ticket.
        QueueID (Optional[int]): Numeric ID of the queue.
        Queue (Optional[str]): Name of the queue.
        StateID (Optional[int]): Numeric ID of the ticket state.
        State (Optional[str]): Name of the ticket state.
        PriorityID (Optional[int]): Numeric ID of the priority.
        Priority (Optional[str]): Name of the priority.
        OwnerID (Optional[int]): Numeric ID of the ticket owner.
        Owner (Optional[str]): User login of the ticket owner.
        CustomerUser (Optional[str]): Login name of the customer user.
    """
    Title: Optional[str] = None
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
    """
    Represents a dynamic field key-value pair for tickets.

    Attributes:
        Name (str): Name of the dynamic field.
        Value (Optional[Any]): Value assigned to the field.
    """
    Name: str
    Value: Optional[Any] = None


class ArticleDetail(BaseModel):
    """
    Detailed model of an article within a ticket.

    Attributes:
        From (Optional[str]): Sender address or login.
        Subject (Optional[str]): Subject line of the article.
        Body (Optional[str]): Content body of the article.
        ContentType (Optional[str]): Content type MIME header.
        CreateTime (Optional[str]): Timestamp when the article was created.
        ChangeTime (Optional[str]): Timestamp of last modification.
        To (Optional[str]): Recipient address or login.
        MessageID (Optional[str]): Message-ID header.
        ChangeBy (Optional[int]): User ID who modified the article.
        CreateBy (Optional[int]): User ID who created the article.
        ArticleID (Optional[int]): Unique article identifier.
        ArticleNumber (Optional[int]): Sequential article number.
    """
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
    ArticleID: Optional[int] = None
    ArticleNumber: Optional[int] = None


class TicketDetailOutput(TicketBase):
    """
    Full ticket model returned by OTOBO including articles and dynamic fields.

    Attributes:
        Article (Union[ArticleDetail,List[ArticleDetail]]): Single or list of article details.
        DynamicField (List[DynamicFieldItem]): List of dynamic field items on the ticket.
    """
    Article: Union[ArticleDetail, List[ArticleDetail]]
    DynamicField: List[DynamicFieldItem]


