import logging
from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel

from otobo_znuny.domain_models.basic_auth_model import BasicAuth
from otobo_znuny.models.base_models import BooleanInteger
from otobo_znuny.domain_models.ticket_models import Article, IdName, TicketBase, TicketSearch, DynamicFieldFilter
from otobo_znuny.domain_models.ticket_models import TicketUpdate, Ticket, TicketCreate
from otobo_znuny.models.request_models import WsTicketMutationRequest, WsTicketUpdateRequest, WsTicketSearchRequest, \
    WsTicketGetRequest, WsDynamicFieldFilter, WsAuthData
from otobo_znuny.models.ticket_models import WsDynamicField, WsArticleDetail, WsTicketOutput, WsTicketBase

logger = logging.getLogger(__name__)


def try_parsing_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    logger.warning(f"Failed to parse datetime: {value}")
    return None


def to_ws_dynamic_field_items(dynamic_fields: dict[str, str]) -> list[WsDynamicField]:
    return [WsDynamicField(Name=key, Value=value) for key, value in dynamic_fields.items()]


def from_ws_dynamic_field_items(dynamic_items: Optional[list[WsDynamicField]]) -> dict[str, str]:
    return {item.Name: item.Value for item in dynamic_items or []}


def _to_str(value: Any) -> str:
    return str(value)


def _to_str_list(values: list[Any]) -> list[str]:
    return [str(v) for v in values]


def to_ws_dynamic_field_search(filter_model: DynamicFieldFilter) -> WsDynamicFieldFilter:
    has_value_constraint = any(
        [
            filter_model.equals is not None,
            filter_model.like is not None,
            filter_model.greater is not None,
            filter_model.smaller is not None,
        ]
    )

    if filter_model.empty is True:
        empty_flag: BooleanInteger = 1
    elif filter_model.empty is False:
        empty_flag = 0
    else:
        empty_flag = 0 if has_value_constraint else 1

    equals_value: Union[str, list[str], None] = None
    if isinstance(filter_model.equals, list):
        equals_value = _to_str_list(filter_model.equals)
    elif filter_model.equals is not None:
        equals_value = _to_str(filter_model.equals)

    like_value = filter_model.like
    greater_value = _to_str(filter_model.greater) if filter_model.greater is not None else None
    smaller_value = _to_str(filter_model.smaller) if filter_model.smaller is not None else None

    return WsDynamicFieldFilter(
        Empty=empty_flag,
        Equals=equals_value,
        Like=like_value,
        GreaterThan=greater_value,
        SmallerThan=smaller_value,
    )


def to_ws_article(article: Article) -> WsArticleDetail:
    return WsArticleDetail(
        From=article.from_addr,
        To=article.to_addr,
        Subject=article.subject,
        Body=article.body,
        ContentType=article.content_type,
    )


def from_ws_article(article_otobo: WsArticleDetail) -> Article:
    return Article(
        from_addr=article_otobo.From,
        to_addr=article_otobo.To,
        subject=article_otobo.Subject,
        body=article_otobo.Body,
        content_type=article_otobo.ContentType,
        created_at=try_parsing_datetime(article_otobo.CreateTime),
        changed_at=try_parsing_datetime(article_otobo.ChangeTime),
        article_id=article_otobo.ArticleID,
        article_number=article_otobo.ArticleNumber,
    )


def _to_id_name(id_value: Optional[int], name_value: Optional[str]) -> Optional[IdName]:
    if id_value is None and name_value is None:
        return None
    return IdName(id=id_value, name=name_value)


def _split_id_name_sequence(items: Optional[list[IdName]]) -> tuple[Optional[list[int]], Optional[list[str]]]:
    if not items:
        return None, None
    id_list = [x.id for x in items if x.id is not None] or None
    name_list = [x.name for x in items if x.name is not None] or None
    return id_list, name_list


def id_name(v: Optional[IdName]) -> tuple[Optional[int], Optional[str]]:
    return (v.id, v.name) if v else (None, None)


def has_any_attribute_set(otobo_ticket_base: BaseModel) -> bool:
    return bool(otobo_ticket_base.model_dump(exclude_none=True))


def from_ws_ticket_detail(ticket_otobo: WsTicketOutput) -> Ticket:
    return Ticket(
        id=ticket_otobo.TicketID,
        number=ticket_otobo.TicketNumber,
        title=ticket_otobo.Title,
        lock=_to_id_name(ticket_otobo.LockID, ticket_otobo.Lock),
        queue=_to_id_name(ticket_otobo.QueueID, ticket_otobo.Queue),
        state=_to_id_name(ticket_otobo.StateID, ticket_otobo.State),
        priority=_to_id_name(ticket_otobo.PriorityID, ticket_otobo.Priority),
        type=_to_id_name(ticket_otobo.TypeID, ticket_otobo.Type),
        owner=_to_id_name(ticket_otobo.OwnerID, ticket_otobo.Owner),
        customer_id=ticket_otobo.CustomerID,
        customer_user=ticket_otobo.CustomerUser,
        created_at=try_parsing_datetime(ticket_otobo.Created),
        changed_at=try_parsing_datetime(ticket_otobo.Changed),
        articles=[from_ws_article(a) for a in ticket_otobo.get_articles()],
    )


def to_ws_ticket_base(ticket: TicketBase) -> Optional[WsTicketBase]:
    queue_id, queue_name = id_name(ticket.queue)
    state_id, state_name = id_name(ticket.state)
    priority_id, priority_name = id_name(ticket.priority)
    type_id, type_name = id_name(ticket.type)
    lock_id, lock_name = id_name(ticket.lock)

    otobo_ticket: WsTicketBase = WsTicketBase(
        Title=ticket.title,
        QueueID=queue_id,
        Queue=queue_name,
        LockID=lock_id,
        Lock=lock_name,
        StateID=state_id,
        State=state_name,
        PriorityID=priority_id,
        Priority=priority_name,
        CustomerUser=ticket.customer_user,
        TypeID=type_id,
        Type=type_name,
    )

    if has_any_attribute_set(otobo_ticket):
        return otobo_ticket
    return None


def to_ws_ticket_create(ticket_domain: TicketCreate) -> WsTicketMutationRequest:
    ticket_base = to_ws_ticket_base(ticket_domain)
    article_otobo = to_ws_article(ticket_domain.article) if ticket_domain.article else None
    return WsTicketMutationRequest(Ticket=ticket_base, Article=article_otobo)


def to_ws_ticket_update(ticket_domain: TicketUpdate) -> WsTicketUpdateRequest:
    ticket_base = to_ws_ticket_base(ticket_domain)
    article_otobo = to_ws_article(ticket_domain.article) if ticket_domain.article else None
    return WsTicketUpdateRequest(
        Ticket=ticket_base,
        Article=article_otobo,
        TicketID=ticket_domain.id,
        TicketNumber=ticket_domain.number,
    )


def to_ws_ticket_search(search_model: TicketSearch) -> WsTicketSearchRequest:
    queue_ids, queue_names = _split_id_name_sequence(search_model.queues)
    state_ids, state_names = _split_id_name_sequence(search_model.states)
    priority_ids, priority_names = _split_id_name_sequence(search_model.priorities)
    type_ids, type_names = _split_id_name_sequence(search_model.types)
    return WsTicketSearchRequest(
        TicketNumber=search_model.numbers,
        Title=search_model.titles,
        Queues=queue_names,
        QueueIDs=queue_ids,
        States=state_names,
        StateIDs=state_ids,
        Priorities=priority_names,
        PriorityIDs=priority_ids,
        Types=type_names,
        TypeIDs=type_ids,
        UseSubQueues=search_model.use_subqueues,
        Limit=search_model.limit,
    )


def to_ws_ticket_get(ticket_id: int) -> WsTicketGetRequest:
    return WsTicketGetRequest(TicketID=ticket_id)


def to_ws_auth(basic_auth: BasicAuth) -> WsAuthData:
    return WsAuthData(
        UserLogin=basic_auth.user_login,
        Password=basic_auth.password,
    )
