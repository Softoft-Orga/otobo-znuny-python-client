# tests/test_mappers.py
import random

import pytest
from datetime import datetime

from otobo.mappers import build_ticket_create_request, parse_ticket_detail_output, build_ticket_update_request, \
    build_ticket_search_request, build_ticket_get_request
from otobo.domain_models.ticket_models import TicketBase, IdName, TicketSearch, Article, TicketCreate, TicketUpdate
from otobo.models.ticket_models import OTOBOTicketBase, ArticleDetail, DynamicFieldItem, TicketDetailOutput
from otobo.models.request_models import TicketCreateRequest, TicketUpdateRequest, TicketGetRequest, TicketSearchRequest


def test_build_ticket_create_request_roundtrip():
    t = TicketCreate(
        title="Demo",
        queue=IdName(id=2, name="Raw"),
        state=IdName(name="new"),
        priority=IdName(name="3 normal"),
        type=IdName(name="Unclassified"),
        customer_user="user1",
        article=Article(subject="S", body="B", content_type="text/plain", from_addr="a@b.c", to_addr="x@y.z"),
    )
    req = build_ticket_create_request(t)
    assert isinstance(req, TicketCreateRequest)
    assert req.Ticket is not None
    req_ticket: OTOBOTicketBase = req.Ticket
    assert req_ticket.Title == "Demo"
    assert req_ticket.QueueID == 2
    assert req_ticket.Queue == "Raw"
    assert req_ticket.State == "new"
    assert req_ticket.Priority == "3 normal"
    assert req_ticket.Type == "Unclassified"
    articles = req.Article if isinstance(req.Article, list) else [req.Article] if req.Article else []
    assert articles[0].Subject == "S"
    assert articles[0].Body == "B"
    wire = TicketDetailOutput(
        Title=req_ticket.Title,
        QueueID=req_ticket.QueueID,
        Queue=req_ticket.Queue,
        State=req_ticket.State,
        Priority=req_ticket.Priority,
        Type=req_ticket.Type,
        CustomerUser=req_ticket.CustomerUser,
        TicketID=111,
        TicketNumber="2025",
        Created=datetime.now().isoformat(),
        Changed=datetime.now().isoformat(),
        Article=req.Article,
        DynamicField=[],
    )
    back = parse_ticket_detail_output(wire)
    assert back.title == "Demo"
    assert back.queue == IdName(id=2, name="Raw")
    assert back.state == IdName(name="new")
    assert back.priority == IdName(name="3 normal")
    assert back.type == IdName(name="Unclassified")
    assert back.customer_user == "user1"
    assert len(back.articles) == 1
    assert back.articles[0].subject == "S"
    assert back.number == "2025"
    assert back.id == 111


def test_build_ticket_update_request_includes_ids_and_names():
    random_ticket_id = random.randint(1, 10**12)
    t = TicketUpdate(
        id=random_ticket_id,
        number="TN-1",
        title="Updated",
        queue=IdName(id=5, name="Support"),
        state=IdName(id=1, name="open"),
        priority=IdName(id=3, name="3 normal"),
        type=IdName(id=2, name="Incident"),
        customer_user="user2",
    )
    req = build_ticket_update_request(t)
    assert req.Ticket is not None
    req_ticket: OTOBOTicketBase = req.Ticket
    assert isinstance(req, TicketUpdateRequest)
    assert req.TicketID == random_ticket_id
    assert req_ticket.Title == "Updated"
    assert req_ticket.QueueID == 5
    assert req_ticket.StateID == 1


def test_build_ticket_search_request_idname_lists() -> None:
    s = TicketSearch(
        numbers=["1001", "1002"],
        titles=["Demo"],
        queues=[IdName(id=2, name="Raw"), IdName(name="Support")],
        states=[IdName(name="open")],
        priorities=[IdName(id=4)],
        types=[IdName(name="Incident")],
        customer_users=["user1", "user2"],
        use_subqueues=True,
        limit=25,
    )
    req = build_ticket_search_request(s)
    assert isinstance(req, TicketSearchRequest)
    assert req.TicketNumber == ["1001", "1002"]
    assert req.Title == ["Demo"]
    assert sorted(req.QueueIDs or []) == [2]
    assert sorted(req.Queues or []) == ["Raw", "Support"]
    assert req.States == ["open"]
    assert req.PriorityIDs == [4]
    assert req.Types == ["Incident"]
    assert req.UseSubQueues == 1


def test_build_ticket_get_request_by_id_and_number() -> None:
    r1 = build_ticket_get_request(ticket_id=7)
    assert isinstance(r1, TicketGetRequest)
    assert r1.TicketID == 7


def test_parse_ticket_detail_output_handles_single_and_list_article() -> None:
    art = ArticleDetail(Subject="S1", Body="B1", ContentType="text/plain")
    wire_single = TicketDetailOutput(
        Title="A",
        TicketID=1,
        TicketNumber="N1",
        Article=art,
        DynamicField=[DynamicFieldItem(Name="K", Value="V")],
    )
    d1 = parse_ticket_detail_output(wire_single)
    assert len(d1.articles) == 1
    assert d1.articles[0].subject == "S1"
    wire_list = TicketDetailOutput(
        Title="A",
        TicketID=2,
        TicketNumber="N2",
        Article=[art, ArticleDetail(Subject="S2", Body="B2", ContentType="text/plain")],
        DynamicField=[],
    )
    d2 = parse_ticket_detail_output(wire_list)
    assert len(d2.articles) == 2
    assert [a.subject for a in d2.articles] == ["S1", "S2"]
