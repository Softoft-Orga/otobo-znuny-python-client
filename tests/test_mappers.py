# tests/test_mappers.py
import pytest
from datetime import datetime

from mappers import build_ticket_create_request, parse_ticket_detail_output, build_ticket_update_request, \
    build_ticket_search_request, build_ticket_get_request
from otobo.domain_models.ticket_models import Ticket, IdName, TicketSearch, Article
from otobo.models.ticket_models import TicketBase, ArticleDetail, DynamicFieldItem, TicketDetailOutput
from otobo.models.request_models import TicketCreateRequest, TicketUpdateRequest, TicketGetRequest, TicketSearchRequest


def test_build_ticket_create_request_roundtrip():
    t = Ticket(
        title="Demo",
        queue=IdName(id=2, name="Raw"),
        state=IdName(name="new"),
        priority=IdName(name="3 normal"),
        type=IdName(name="Unclassified"),
        customer_user="user1",
        dynamic_fields={"X": "Y", "Flag": 1},
        articles=[Article(subject="S", body="B", content_type="text/plain", from_addr="a@b.c", to_addr="x@y.z")],
    )
    req = build_ticket_create_request(t)
    assert isinstance(req, TicketCreateRequest)
    assert req.Ticket.Title == "Demo"
    assert req.Ticket.QueueID == 2
    assert req.Ticket.Queue == "Raw"
    assert req.Ticket.State == "new"
    assert req.Ticket.Priority == "3 normal"
    assert req.Ticket.Type == "Unclassified"
    df = {i.Name: i.Value for i in req.DynamicField or []}
    assert df == {"X": "Y", "Flag": 1}
    assert req.Article.Subject == "S"
    assert req.Article.Body == "B"
    wire = TicketDetailOutput(
        Title=req.Ticket.Title,
        QueueID=req.Ticket.QueueID,
        Queue=req.Ticket.Queue,
        State=req.Ticket.State,
        Priority=req.Ticket.Priority,
        Type=req.Ticket.Type,
        CustomerUser=req.Ticket.CustomerUser,
        TicketID=111,
        TicketNumber="2025",
        Created=datetime.utcnow().isoformat(),
        Changed=datetime.utcnow().isoformat(),
        Article=req.Article,
        DynamicField=req.DynamicField,
    )
    back = parse_ticket_detail_output(wire)
    assert back.title == "Demo"
    assert back.queue == IdName(id=2, name="Raw")
    assert back.state == IdName(name="new")
    assert back.priority == IdName(name="3 normal")
    assert back.type == IdName(name="Unclassified")
    assert back.customer_user == "user1"
    assert back.dynamic_fields == {"X": "Y", "Flag": 1}
    assert len(back.articles) == 1
    assert back.articles[0].subject == "S"
    assert back.number == "2025"
    assert back.id == 111


def test_build_ticket_update_request_includes_ids_and_names():
    t = Ticket(
        id=123,
        number="TN-1",
        title="Updated",
        queue=IdName(id=5, name="Support"),
        state=IdName(id=1, name="open"),
        priority=IdName(id=3, name="3 normal"),
        type=IdName(id=2, name="Incident"),
        customer_user="user2",
        dynamic_fields={"A": "B"},
    )
    req = build_ticket_update_request(t, fields_to_update=["Title", "QueueID", "StateID"])
    assert isinstance(req, TicketUpdateRequest)
    assert req.TicketID == 123
    assert req.Ticket.Title == "Updated"
    assert req.Ticket.QueueID == 5
    assert req.Ticket.StateID == 1
    df = {i.Name: i.Value for i in req.DynamicField or []}
    assert df == {"A": "B"}


def test_build_ticket_search_request_idname_lists():
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
    assert req.CustomerUserLogin == ["user1", "user2"]
    assert req.UseSubQueues == 1


def test_build_ticket_get_request_by_id_and_number():
    r1 = build_ticket_get_request(ticket_id=7)
    assert isinstance(r1, TicketGetRequest)
    assert r1.TicketID == 7
    assert r1.TicketNumber is None
    r2 = build_ticket_get_request(ticket_number="T-42")
    assert r2.TicketID is None
    assert r2.TicketNumber == "T-42"


def test_parse_ticket_detail_output_handles_single_and_list_article():
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
