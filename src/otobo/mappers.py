from typing import Any

from otobo.domain_models.ticket_models import Article, IdName, Ticket, TicketSearch
from otobo.models.ticket_models import DynamicFieldItem, ArticleDetail, TicketDetailOutput, TicketBase
from otobo import TicketCreateRequest, TicketUpdateRequest, TicketSearchRequest, TicketGetRequest


def _dynamic_fields_dict_to_items(dynamic_fields: dict[str, Any]) -> list[DynamicFieldItem]:
    return [DynamicFieldItem(Name=key, Value=value) for key, value in dynamic_fields.items()]


def _dynamic_fields_items_to_dict(dynamic_items: list[DynamicFieldItem] | None) -> dict[str, Any]:
    return {item.Name: item.Value for item in dynamic_items or []}


def _article_domain_to_wire(article: Article) -> ArticleDetail:
    return ArticleDetail(
        From=article.from_addr,
        To=article.to_addr,
        Subject=article.subject,
        Body=article.body,
        ContentType=article.content_type,
    )


def _article_wire_to_domain(article_wire: ArticleDetail) -> Article:
    return Article(
        from_addr=article_wire.From,
        to_addr=article_wire.To,
        subject=article_wire.Subject,
        body=article_wire.Body,
        content_type=article_wire.ContentType,
        created_at=article_wire.CreateTime,
        changed_at=article_wire.ChangeTime,
        article_id=article_wire.ArticleID,
        article_number=article_wire.ArticleNumber,
    )


def _to_idname(id_value: int | None, name_value: str | None) -> IdName | None:
    if id_value is None and name_value is None:
        return None
    return IdName(id=id_value, name=name_value)


def _split_idname_sequence(items: list[IdName] | None) -> tuple[list[int] | None, list[str] | None]:
    if not items:
        return None, None
    id_list = [x.id for x in items if x.id is not None] or None
    name_list = [x.name for x in items if x.name is not None] or None
    return id_list, name_list


def parse_ticket_detail_output(ticket_wire: TicketDetailOutput) -> Ticket:
    wire_articles = ticket_wire.Article \
        if isinstance(ticket_wire.Article, list) \
        else [ticket_wire.Article] if ticket_wire.Article else []
    return Ticket(
        id=ticket_wire.TicketID,
        number=ticket_wire.TicketNumber,
        title=ticket_wire.Title,
        queue=_to_idname(ticket_wire.QueueID, ticket_wire.Queue),
        state=_to_idname(ticket_wire.StateID, ticket_wire.State),
        priority=_to_idname(ticket_wire.PriorityID, ticket_wire.Priority),
        type=_to_idname(ticket_wire.TypeID, ticket_wire.Type),
        owner=_to_idname(ticket_wire.OwnerID, ticket_wire.Owner),
        customer_id=ticket_wire.CustomerID,
        customer_user=ticket_wire.CustomerUser,
        created_at=ticket_wire.Created,
        changed_at=ticket_wire.Changed,
        articles=[_article_wire_to_domain(a) for a in wire_articles],
    )


def build_ticket_base(ticket_domain: Ticket) -> TicketBase:
    return TicketBase(
        Title=ticket_domain.title,
        QueueID=ticket_domain.queue.id if ticket_domain.queue else None,
        Queue=ticket_domain.queue.name if ticket_domain.queue else None,
        StateID=ticket_domain.state.id if ticket_domain.state else None,
        State=ticket_domain.state.name if ticket_domain.state else None,
        PriorityID=ticket_domain.priority.id if ticket_domain.priority else None,
        Priority=ticket_domain.priority.name if ticket_domain.priority else None,
        CustomerUser=ticket_domain.customer_user,
        TypeID=ticket_domain.type.id if ticket_domain.type else None,
        Type=ticket_domain.type.name if ticket_domain.type else None,
    )


def build_ticket_create_request(ticket_domain: Ticket) -> TicketCreateRequest:
    ticket_base = build_ticket_base(ticket_domain)
    article_wire = [_article_domain_to_wire(article) for article in
                    ticket_domain.articles] if ticket_domain.articles else []
    return TicketCreateRequest(Ticket=ticket_base, Article=article_wire)


def build_ticket_update_request(ticket_domain: Ticket) -> TicketUpdateRequest:
    ticket_base = build_ticket_base(ticket_domain)

    article_wire = _article_domain_to_wire(ticket_domain.articles[0]) if ticket_domain.articles else None
    return TicketUpdateRequest(
        Ticket=ticket_base,
        Article=article_wire,
        DynamicField=[],
        TicketID=ticket_domain.id,
        TicketNumber=ticket_domain.number,
    )


def build_ticket_search_request(search_model: TicketSearch) -> TicketSearchRequest:
    queue_ids, queue_names = _split_idname_sequence(search_model.queues)
    state_ids, state_names = _split_idname_sequence(search_model.states)
    priority_ids, priority_names = _split_idname_sequence(search_model.priorities)
    type_ids, type_names = _split_idname_sequence(search_model.types)
    return TicketSearchRequest(
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
    )


def build_ticket_get_request(ticket_id: int) -> TicketGetRequest:
    return TicketGetRequest(TicketID=ticket_id)
