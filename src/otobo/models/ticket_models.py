from typing import Any, List, Union, Optional
from pydantic import BaseModel


class AttachmentModel(BaseModel):
    """
    Model representing an attachment to be sent with a ticket operation.

    Attributes:
        Filename (str): Name of the file including extension.
        ContentType (Optional[str]): MIME type of the file (e.g., 'application/pdf').
        Content (Optional[str]): Base64-encoded content of the file.
    """
    Filename: str
    ContentType: Optional[str] = None
    Content: Optional[str] = None


class AttachmentResponseDetail(AttachmentModel):
    """
    Detailed model for an attachment returned by OTOBO.

    Attributes:
        ContentAlternative (Optional[str]): Alternative content representation.
        ContentID (Optional[str]): Identifier for inline content references.
        Filesize (Optional[str]): Human-readable file size (e.g., '15 KB').
        FilesizeRaw (Optional[int]): File size in bytes.
    """
    ContentAlternative: Optional[str] = None
    ContentID: Optional[str] = None
    Filesize: Optional[str] = None
    FilesizeRaw: Optional[int] = None


class TicketBase(BaseModel):
    """
    Common fields for ticket creation and updates.

    Attributes:
        Title (Optional[str]): Subject or title of the ticket.
        QueueID (Optional[int]): Numeric ID of the queue.
        Queue (Optional[str]): Name of the queue.
        LockID (Optional[int]): Numeric ID of the lock status.
        Lock (Optional[str]): Name of the lock status.
        TypeID (Optional[int]): Numeric ID of the ticket type.
        Type (Optional[str]): Name of the ticket type.
        ServiceID (Optional[Union[int,str]]): Numeric or string ID of the service.
        Service (Optional[str]): Name of the service.
        SLAID (Optional[Union[int,str]]): Numeric or string ID of the SLA.
        SLA (Optional[str]): Name of the SLA.
        StateID (Optional[int]): Numeric ID of the ticket state.
        State (Optional[str]): Name of the ticket state.
        PriorityID (Optional[int]): Numeric ID of the priority.
        Priority (Optional[str]): Name of the priority.
        OwnerID (Optional[int]): Numeric ID of the ticket owner.
        Owner (Optional[str]): User login of the ticket owner.
        ResponsibleID (Optional[int]): Numeric ID of the responsible agent.
        Responsible (Optional[str]): User login of the responsible agent.
        CustomerUser (Optional[str]): Login name of the customer user.
    """
    Title: Optional[str] = None
    QueueID: Optional[int] = None
    Queue: Optional[str] = None
    LockID: Optional[int] = None
    Lock: Optional[str] = None
    TypeID: Optional[int] = None
    Type: Optional[str] = None
    ServiceID: Optional[Union[int, str]] = None
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
    """
    Extended ticket fields common to detailed output.

    Attributes:
        Title (Optional[str]): Subject or title of the ticket.
        QueueID (Optional[int]): Numeric ID of the queue.
        Queue (Optional[str]): Name of the queue.
        LockID (Optional[int]): Numeric ID of the lock status.
        Lock (Optional[str]): Name of the lock status.
        TypeID (Optional[int]): Numeric ID of the ticket type.
        Type (Optional[str]): Name of the ticket type.
        ServiceID (Optional[Union[int,str]]): Numeric or string ID of the service.
        Service (Optional[str]): Name of the service.
        SLAID (Optional[Union[int,str]]): Numeric or string ID of the SLA.
        SLA (Optional[str]): Name of the SLA.
        StateID (Optional[int]): Numeric ID of the ticket state.
        State (Optional[str]): Name of the ticket state.
        PriorityID (Optional[int]): Numeric ID of the priority.
        Priority (Optional[str]): Name of the priority.
        OwnerID (Optional[int]): Numeric ID of the ticket owner.
        Owner (Optional[str]): User login of the ticket owner.
        ResponsibleID (Optional[int]): Numeric ID of the responsible agent.
        Responsible (Optional[str]): User login of the responsible agent.
        CustomerUser (Optional[str]): Login name of the customer user.
        TicketID (Optional[int]): Unique identifier of the ticket.
        TicketNumber (Optional[str]): Human-readable ticket number.
        StateType (Optional[str]): Type of the state (e.g., 'open', 'closed').
        CustomerID (Optional[str]): Identifier for the customer.
        CustomerUserID (Optional[str]): Numeric ID of the customer user.
        ArchiveFlag (Optional[str]): Archive status flag.
        Age (Optional[int]): Age of the ticket in seconds.
        EscalationResponseTime (Optional[int]): Configured response escalation time.
        EscalationUpdateTime (Optional[int]): Configured update escalation time.
        EscalationSolutionTime (Optional[int]): Configured solution escalation time.
        EscalationTime (Optional[int]): Total escalation time configured.
        CreateBy (Optional[int]): User ID who created the ticket.
        ChangeBy (Optional[int]): User ID who last modified the ticket.
        Created (Optional[str]): Timestamp when the ticket was created.
        Changed (Optional[str]): Timestamp when the ticket was last changed.
    """
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
        CommunicationChannel (Optional[str]): Channel of communication (e.g., 'email').
        CommunicationChannelID (Optional[int]): Numeric ID of the channel.
        IsVisibleForCustomer (Optional[int]): Visibility flag for the customer.
        SenderTypeID (Optional[Union[int,str]]): Numeric or string ID of sender type.
        AutoResponseType (Optional[str]): Type of auto-response triggered.
        From (Optional[str]): Sender address or login.
        Subject (Optional[str]): Subject line of the article.
        Body (Optional[str]): Content body of the article.
        ContentType (Optional[str]): Content type MIME header.
        MimeType (Optional[str]): MIME type string.
        Charset (Optional[str]): Character set encoding.
        CreateTime (Optional[str]): Timestamp when the article was created.
        ChangeTime (Optional[str]): Timestamp of last modification.
        IncomingTime (Optional[int]): Unix timestamp of incoming message.
        To (Optional[str]): Recipient address or login.
        SenderType (Optional[str]): Description of sender type.
        IsEdited (Optional[int]): Edit flag indicator.
        Cc (Optional[str]): Carbon copy recipients.
        Bcc (Optional[str]): Blind carbon copy recipients.
        ReplyTo (Optional[str]): Reply-to address.
        InReplyTo (Optional[str]): In-reply-to message ID.
        References (Optional[str]): References header links.
        MessageID (Optional[str]): Message-ID header.
        ContentCharset (Optional[str]): Content charset header.
        ChangeBy (Optional[int]): User ID who modified the article.
        CreateBy (Optional[int]): User ID who created the article.
        IsDeleted (Optional[int]): Deletion flag indicator.
        ArticleID (Optional[int]): Unique article identifier.
        ArticleNumber (Optional[int]): Sequential article number.
        DynamicField (Optional[List[DynamicFieldItem]]): List of dynamic fields.
        Attachment (Optional[AttachmentResponseDetail]): Attached file details.
    """
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
    """
    Full ticket model returned by OTOBO including articles and dynamic fields.

    Attributes:
        Article (Union[ArticleDetail,List[ArticleDetail]]): Single or list of article details.
        DynamicField (List[DynamicFieldItem]): List of dynamic field items on the ticket.
    """
    Article: Union[ArticleDetail, List[ArticleDetail]]
    DynamicField: List[DynamicFieldItem]


class TicketDetailInput(BaseModel):
    """
    Model for creating or updating a ticket, includes optional details.

    Attributes:
        Ticket (Optional[TicketCommon]): Core ticket fields to set.
        Article (Optional[Union[ArticleDetail,List[ArticleDetail]]]): Article(s) to attach.
        DynamicField (Optional[List[DynamicFieldItem]]): Dynamic fields to set.
        Attachment (Optional[AttachmentModel]): Single attachment to include.
    """
    Ticket: Optional[TicketCommon] = None
    Article: Optional[Union[ArticleDetail, List[ArticleDetail]]] = None
    DynamicField: Optional[List[DynamicFieldItem]] = None
    Attachment: Optional[AttachmentModel] = None
