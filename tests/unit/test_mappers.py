# tests/test_mappers.py
import random
from datetime import datetime

import pytest

from otobo_znuny_python_client.domain_models.ticket_models import (
    Article,
    IdName,
    TicketCreate,
    TicketSearch,
    TicketUpdate,
)
from otobo_znuny_python_client.mappers import (
    from_ws_ticket_detail,
    to_ws_ticket_create,
    to_ws_ticket_search,
    to_ws_ticket_update,
)
from otobo_znuny_python_client.models.request_models import (
    WsTicketMutationRequest,
    WsTicketSearchRequest,
    WsTicketUpdateRequest,
)
from otobo_znuny_python_client.models.ticket_models import (
    WsArticleDetail,
    WsDynamicField,
    WsTicketBase,
    WsTicketOutput,
)


@pytest.mark.unit
def test_build_ticket_create_request_roundtrip() -> None:
    t = TicketCreate(
        title="Demo",
        queue=IdName(id=2, name="Raw"),
        state=IdName(name="new"),
        priority=IdName(name="3 normal"),
        type=IdName(name="Unclassified"),
        customer_user="user1",
        article=Article(subject="S", body="B", content_type="text/plain", from_addr="a@b.c", to_addr="x@y.z"),
    )
    req: WsTicketMutationRequest = to_ws_ticket_create(t)
    assert isinstance(req, WsTicketMutationRequest)
    assert req.Ticket is not None
    req_ticket: WsTicketBase = req.Ticket
    assert req_ticket.Title == "Demo"
    assert req_ticket.QueueID == 2
    assert req_ticket.Queue == "Raw"
    assert req_ticket.State == "new"
    assert req_ticket.Priority == "3 normal"
    assert req_ticket.Type == "Unclassified"
    assert req_ticket.CustomerUser == "user1"
    articles = req.Article if isinstance(req.Article, list) else [req.Article] if req.Article else []
    assert articles[0].Subject == "S"
    assert articles[0].Body == "B"
    wire = WsTicketOutput(
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
        Article=articles,
        DynamicField=[],
    )
    back = from_ws_ticket_detail(wire)
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


@pytest.mark.unit
def test_build_ticket_update_request_includes_ids_and_names() -> None:
    random_ticket_id = random.randint(1, 10 ** 12)
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
    req = to_ws_ticket_update(t)
    assert req.Ticket is not None
    req_ticket: WsTicketBase = req.Ticket
    assert isinstance(req, WsTicketUpdateRequest)
    assert req.TicketID == random_ticket_id
    assert req_ticket.Title == "Updated"
    assert req_ticket.QueueID == 5
    assert req_ticket.StateID == 1


@pytest.mark.unit
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
    req = to_ws_ticket_search(s)
    assert isinstance(req, WsTicketSearchRequest)
    assert req.TicketNumber == ["1001", "1002"]
    assert req.Title == ["Demo"]
    assert sorted(req.QueueIDs or []) == [2]
    assert sorted(req.Queues or []) == ["Raw", "Support"]
    assert req.States == ["open"]
    assert req.PriorityIDs == [4]
    assert req.Types == ["Incident"]
    assert req.UseSubQueues == 1


@pytest.mark.unit
def test_parse_ticket_detail_output_handles_single_and_list_article() -> None:
    art = WsArticleDetail(Subject="S1", Body="B1", ContentType="text/plain")
    wire_single = WsTicketOutput(
        Title="A",
        TicketID=1,
        TicketNumber="N1",
        Article=[art],
        DynamicField=[WsDynamicField(Name="K", Value="V")],
    )
    d1 = from_ws_ticket_detail(wire_single)
    assert len(d1.articles) == 1
    assert d1.articles[0].subject == "S1"
    wire_list = WsTicketOutput(
        Title="A",
        TicketID=2,
        TicketNumber="N2",
        Article=[art, WsArticleDetail(Subject="S2", Body="B2", ContentType="text/plain")],
        DynamicField=[],
    )
    d2 = from_ws_ticket_detail(wire_list)
    assert len(d2.articles) == 2
    assert [a.subject for a in d2.articles] == ["S1", "S2"]
