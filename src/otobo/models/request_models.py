from typing import Optional, Union, List, Dict, Literal

from pydantic import BaseModel, Field

"""Pydantic models for request payloads sent to the OTOBO API."""

from otobo.models.ticket_models import TicketBase, ArticleDetail, DynamicFieldItem


class AuthData(BaseModel):
    """
    Authentication credentials for OTOBO Webservice API.

    Attributes:
        SessionID (Optional[int]): Optional session identifier for existing sessions.
        UserLogin (str): Agent login name for authentication.
        Password (str): Agent password for authentication.
    """
    SessionID: Optional[int] = None
    UserLogin: str = Field(..., description="Agent login for authentication")
    Password: str = Field(..., description="Agent password for authentication")



class TicketSearchRequest(BaseModel):
    """
    Search filters for querying tickets via OTOBO Webservice.

    Attributes:
            TicketNumber: Optional[Union[str, List[str]]] = None
            Title: Optional[Union[str, List[str]]] = None
            Queues: Optional[List[str]] = None
            QueueIDs: Optional[List[int]] = None
            UseSubQueues: Optional[bool] = None
            Types: Optional[List[str]] = None
            TypeIDs: Optional[List[int]] = None
            States: Optional[List[str]] = None
            StateIDs: Optional[List[int]] = None
            Priorities: Optional[List[str]] = None
            PriorityIDs: Optional[List[int]] = None
    """
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
    """
    Parameters for retrieving a ticket by ID with optional article and attachment controls.

    Attributes:
        TicketID (Optional[int]): ID of the ticket to fetch.
        DynamicFields (int): Include dynamic fields (1 to include).
        Extended (int): Include extended data (1 to include).
        AllArticles (int): Include all articles (1 to include).
        ArticleSenderType (Optional[List[str]]): Filter articles by sender type.
        ArticleOrder (Literal['ASC','DESC']): Order of articles, 'ASC' or 'DESC'.
        ArticleLimit (int): Max number of articles to return.
        Attachments (int): Include attachments metadata (1 to include).
        GetAttachmentContents (int): Include attachment contents (1 to include).
        HTMLBodyAsAttachment (int): Include HTML body as attachment (1 to include).
    """
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
    """
    Model for creating or updating a ticket, includes optional details.

    Attributes:
        Ticket (Optional[TicketBase]): Core ticket fields to set.
        Article (Optional[Union[ArticleDetail,List[ArticleDetail]]]): Article(s) to attach.
        DynamicField (Optional[List[DynamicFieldItem]]): Dynamic fields to set.
    """
    Ticket: Optional[TicketBase] = None
    Article: Optional[Union[ArticleDetail, List[ArticleDetail]]] = None
    DynamicField: Optional[List[DynamicFieldItem]] = None


class TicketUpdateRequest(TicketCreateRequest):
    """
    Parameters for updating an existing ticket, extends TicketDetailInput.

    Attributes:
        TicketID (Optional[int]): ID of the ticket to update.
        TicketNumber (Optional[str]): Number of the ticket to update.
        Ticket (Optional[TicketCommon]): Core ticket fields to set.
        Article (Optional[Union[ArticleDetail,List[ArticleDetail]]]): Article(s) to attach.
        DynamicField (Optional[List[DynamicFieldItem]]): Dynamic fields to set.
    """
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
