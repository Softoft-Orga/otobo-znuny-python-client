# --- Common Ticket fields ---
from typing import Any, List, Union
from typing import Optional

from pydantic import BaseModel



class AttachmentModel(BaseModel):
    Filename: str
    ContentType: Optional[str] = None
    Content: Optional[str] = None  # Base64 encoded content


class AttachmentResponseDetail(AttachmentModel):
    """
        Content            => "xxxx",     # actual attachment contents, base64 enconded
    ContentAlternative => "",
    ContentID          => "",
    ContentType        => "application/pdf",
    Filename           => "StdAttachment-Test1.pdf",
    Filesize           => "4.6 KBytes",
    FilesizeRaw        => 4722,
    """
    ContentAlternative: Optional[str] = None
    ContentID: Optional[str] = None
    Filesize: Optional[str] = None
    FilesizeRaw: Optional[int] = None


class TicketBase(BaseModel):
    Title: Optional[str] = None
    QueueID: Optional[int] = None
    Queue: Optional[str] = None
    LockID: Optional[int] = None
    Lock: Optional[str] = None
    TypeID: Optional[int] = None
    Type: Optional[str] = None
    ServiceID: Optional[Union[int, str]]= None
    Service: Optional[str] = None
    SLAID: Optional[Union[int, str]] = None
    SLA: Optional[str] = None
    StateID: Optional[int] = None
    State: Optional[str] = None
    PriorityID: Optional[int] = None
    Priority: Optional[str] = None
    OwnerID: Optional[int] = None
    Owner: Optional[str] = None
    ResponsibleID: Optional[int] = None
    Responsible: Optional[str] = None
    CustomerUser: Optional[str] = None


class TicketCommon(TicketBase):
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
    StateType: Optional[str] = None
    CustomerID: Optional[str] = None
    CustomerUserID: Optional[str] = None
    ArchiveFlag: Optional[str] = None
    Age: Optional[int] = None
    EscalationResponseTime: Optional[int] = None
    EscalationUpdateTime: Optional[int] = None
    EscalationSolutionTime: Optional[int] = None
    EscalationTime: Optional[int] = None
    CreateBy: Optional[int] = None
    ChangeBy: Optional[int] = None
    Created: Optional[str] = None
    Changed: Optional[str] = None


# --- Models for Ticket Create Response ---
class DynamicFieldItem(BaseModel):
    Name: str
    Value: Optional[Any] = None


from typing import Optional, Union
from pydantic import BaseModel


class ArticleDetail(BaseModel):
    CommunicationChannel: Optional[str] = None
    CommunicationChannelID: Optional[int] = None
    IsVisibleForCustomer: Optional[int] = None
    SenderTypeID: Optional[Union[int, str]] = None
    AutoResponseType: Optional[str] = None
    From: Optional[str] = None
    Subject: Optional[str] = None
    Body: Optional[str] = None
    ContentType: Optional[str] = None
    MimeType: Optional[str] = None
    Charset: Optional[str] = None
    CreateTime: Optional[str] = None
    ChangeTime: Optional[str] = None
    IncomingTime: Optional[int] = None
    To: Optional[str] = None
    SenderType: Optional[str] = None
    IsEdited: Optional[int] = None
    Cc: Optional[str] = None
    Bcc: Optional[str] = None
    ReplyTo: Optional[str] = None
    InReplyTo: Optional[str] = None
    References: Optional[str] = None
    MessageID: Optional[str] = None
    ContentCharset: Optional[str] = None
    ChangeBy: Optional[int] = None
    CreateBy: Optional[int] = None
    IsDeleted: Optional[int] = None
    ArticleID: Optional[int] = None
    ArticleNumber: Optional[int] = None
    DynamicField: Optional[List[DynamicFieldItem]] = None
    Attachment: Optional[AttachmentResponseDetail] = None


class TicketDetailOutput(TicketCommon):
    Article: Union[ArticleDetail, List[ArticleDetail]]
    DynamicField: List[DynamicFieldItem]

class TicketDetailInput(BaseModel):
    Ticket: Optional[TicketCommon] = None
    Article: Optional[Union[ArticleDetail, List[ArticleDetail]]] = None
    DynamicField: Optional[List[DynamicFieldItem]]= None
    Attachment: Optional[AttachmentModel] = None