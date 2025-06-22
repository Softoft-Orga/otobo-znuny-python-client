from typing import Optional, Union, List, Dict, Literal

from pydantic import BaseModel, Field

from models.ticket_models import TicketDetailInput


class AuthData(BaseModel):
    SessionID: Optional[int] = None
    UserLogin: str = Field(..., description="Agent login for authentication")
    Password: str = Field(..., description="Agent password for authentication")


class DynamicFieldParams(BaseModel):
    Empty: Optional[bool] = None
    Equals: Optional[Union[int, str, List[Union[int, str]]]] = None
    Like: Optional[str] = None
    GreaterThan: Optional[str] = None
    GreaterThanEquals: Optional[str] = None
    SmallerThan: Optional[str] = None
    SmallerThanEquals: Optional[str] = None


class TicketSearchParams(BaseModel):
    TicketNumber: Optional[Union[str, List[str]]] = None
    Title: Optional[Union[str, List[str]]] = None
    Queues: Optional[List[str]] = None
    QueueIDs: Optional[List[int]] = None
    UseSubQueues: Optional[bool] = None
    Types: Optional[List[str]] = None
    TypeIDs: Optional[List[int]] = None
    States: Optional[List[str]] = None
    StateIDs: Optional[List[int]] = None
    StateType: Optional[Union[str, List[str]]] = None
    StateTypeIDs: Optional[List[int]] = None
    Priorities: Optional[List[str]] = None
    PriorityIDs: Optional[List[int]] = None
    Services: Optional[List[str]] = None
    ServiceIDs: Optional[List[int]] = None
    SLAs: Optional[List[str]] = None
    SLAIDs: Optional[List[int]] = None
    Locks: Optional[List[str]] = None
    LockIDs: Optional[List[int]] = None
    OwnerIDs: Optional[List[int]] = None
    ResponsibleIDs: Optional[List[int]] = None
    WatchUserIDs: Optional[List[int]] = None
    CustomerID: Optional[Union[str, List[str]]] = None
    CustomerIDRaw: Optional[Union[str, List[str]]] = None
    CustomerUserLogin: Optional[Union[str, List[str]]] = None
    CreatedUserIDs: Optional[List[int]] = None
    CreatedTypes: Optional[List[str]] = None
    CreatedTypeIDs: Optional[List[int]] = None
    CreatedPriorities: Optional[List[str]] = None
    CreatedPriorityIDs: Optional[List[int]] = None
    CreatedStates: Optional[List[str]] = None
    CreatedStateIDs: Optional[List[int]] = None
    CreatedQueues: Optional[List[str]] = None
    CreatedQueueIDs: Optional[List[int]] = None
    DynamicFields: Optional[Dict[str, DynamicFieldParams]] = None
    MIMEBase_From: Optional[str] = None
    MIMEBase_To: Optional[str] = None
    MIMEBase_Cc: Optional[str] = None
    MIMEBase_Subject: Optional[str] = None
    MIMEBase_Body: Optional[str] = None
    AttachmentName: Optional[str] = None
    FullTextIndex: Optional[bool] = None
    ContentSearch: Optional[str] = None
    ConditionInline: Optional[bool] = None
    ArticleCreateTimeOlderMinutes: Optional[int] = None
    ArticleCreateTimeNewerMinutes: Optional[int] = None
    ArticleCreateTimeNewerDate: Optional[str] = None
    ArticleCreateTimeOlderDate: Optional[str] = None
    TicketCreateTimeOlderMinutes: Optional[int] = None
    TicketCreateTimeNewerMinutes: Optional[int] = None
    TicketCreateTimeNewerDate: Optional[str] = None
    TicketCreateTimeOlderDate: Optional[str] = None
    TicketChangeTimeOlderMinutes: Optional[int] = None
    TicketChangeTimeNewerMinutes: Optional[int] = None
    TicketLastChangeTimeOlderMinutes: Optional[int] = None
    TicketLastChangeTimeNewerMinutes: Optional[int] = None
    TicketLastChangeTimeNewerDate: Optional[str] = None
    TicketLastChangeTimeOlderDate: Optional[str] = None
    TicketChangeTimeNewerDate: Optional[str] = None
    TicketChangeTimeOlderDate: Optional[str] = None
    TicketCloseTimeOlderMinutes: Optional[int] = None
    TicketCloseTimeNewerMinutes: Optional[int] = None
    TicketCloseTimeNewerDate: Optional[str] = None
    TicketCloseTimeOlderDate: Optional[str] = None
    TicketPendingTimeOlderMinutes: Optional[int] = None
    TicketPendingTimeNewerMinutes: Optional[int] = None
    TicketPendingTimeNewerDate: Optional[str] = None
    TicketPendingTimeOlderDate: Optional[str] = None
    TicketEscalationTimeOlderMinutes: Optional[int] = None
    TicketEscalationTimeNewerMinutes: Optional[int] = None
    TicketEscalationTimeNewerDate: Optional[str] = None
    TicketEscalationTimeOlderDate: Optional[str] = None
    SearchInArchive: Optional[str] = None
    OrderBy: Optional[Union[str, List[str]]] = None
    SortBy: Optional[Union[str, List[str]]] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        df = data.pop("DynamicFields", {}) or {}
        for name, params in df.items():
            data[f"DynamicField_{name}"] = params
        return data


class TicketCreateParams(TicketDetailInput):
    pass


class TicketGetParams(BaseModel):
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


class TicketHistoryParams(BaseModel):
    TicketID: str


class TicketUpdateParams(TicketDetailInput):
    TicketID: Optional[int] = None
    TicketNumber: Optional[str] = None
