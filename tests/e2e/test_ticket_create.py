# tests/test_ticket_create_basic.py
import time
from textwrap import dedent
import pytest

from otobo.domain_models.ticket_models import Ticket, IdName, Article
from otobo.models.ticket_models import ArticleDetail, TicketBase
from otobo.models.request_models import TicketCreateRequest, TicketGetRequest


@pytest.mark.asyncio
async def test_create_and_get_ticket_domain(otobo_client):
    title = f"plain-{int(time.time())}"
    created = await otobo_client.create_ticket(
        Ticket(
            title=title,
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            articles=[Article(subject="Plain", body="Hello world", content_type="text/plain; charset=utf-8")],
        )
    )
    assert created.id is not None and created.number
    got = await otobo_client.get_ticket(ticket_id=created.id)
    assert got.title == title
    assert got.queue and got.queue.name == "Raw"
    assert got.state and got.state.name == "new"
    assert got.priority and got.priority.name == "3 normal"
    assert got.type and got.type.name == "Incident"
    assert got.articles and "Hello world" in (got.articles[0].body or "")

@pytest.mark.asyncio
async def test_update_title_and_priority_domain(otobo_client):
    title = f"upd-{int(time.time())}"
    created = await otobo_client.create_ticket(
        Ticket(
            title=title,
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            articles=[Article(subject="init", body="init-body", content_type="text/plain; charset=utf-8")],
        )
    )
    tid = created.id
    updated = await otobo_client.update_ticket(
        Ticket(
            id=tid,
            title=title + "-updated",
            priority=IdName(name="4 high"),
        )
    )
    assert updated.title == title + "-updated"
    assert updated.priority and (updated.priority.name == "4 high" or updated.priority.id == 4)
    got = await otobo_client.get_ticket(ticket_id=tid)
    assert got.title == title + "-updated"
    assert got.priority and (got.priority.name == "4 high" or got.priority.id == 4)

@pytest.mark.asyncio
async def test_update_add_article_domain(otobo_client):
    title = f"updart-{int(time.time())}"
    created = await otobo_client.create_ticket(
        Ticket(
            title=title,
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            articles=[Article(subject="init", body="init", content_type="text/plain; charset=utf-8")],
        )
    )
    tid = created.id
    note_body = "added-note-body"
    updated = await otobo_client.update_ticket(
        Ticket(
            id=tid,
            articles=[Article(subject="note", body=note_body, content_type="text/plain; charset=utf-8")],
        )
    )
    assert updated.id == tid
    got = await otobo_client.get_ticket(ticket_id=tid)
    assert any(note_body in (a.body or "") for a in got.articles)

