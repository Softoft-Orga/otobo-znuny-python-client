# tests/test_ticket_create_basic.py
import time

import pytest

from otobo_znuny_python_client.clients.otobo_client import OTOBOZnunyClient
from otobo_znuny_python_client.domain_models.ticket_models import Article, IdName, TicketCreate, TicketUpdate


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_and_get_ticket_domain(otobo_client: OTOBOZnunyClient) -> None:
    title = f"plain-{int(time.time())}"
    created = await otobo_client.create_ticket(
        TicketCreate(
            title=title,
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="Plain", body="Hello world", content_type="text/plain; charset=utf-8"),
        ),
    )
    assert created.id is not None
    assert created.number
    got = await otobo_client.get_ticket(ticket_id=created.id)
    assert got.title == title
    assert got.queue
    assert got.queue.name == "Raw"
    assert got.state
    assert got.state.name == "new"
    assert got.priority
    assert got.priority.name == "3 normal"
    assert got.type
    assert got.type.name == "Incident"
    assert got.articles
    assert "Hello world" in (got.articles[0].body or "")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_title_and_priority_domain(otobo_client: OTOBOZnunyClient) -> None:
    title = f"upd-{int(time.time())}"
    created = await otobo_client.create_ticket(
        TicketCreate(
            title=title,
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="init", body="init-body", content_type="text/plain; charset=utf-8"),
        ),
    )
    tid = created.id
    updated = await otobo_client.update_ticket(
        TicketUpdate(
            id=tid,
            title=title + "-updated",
            priority=IdName(name="4 high"),
        ),
    )
    assert updated.title == title + "-updated"
    assert updated.priority
    assert (updated.priority.name == "4 high" or updated.priority.id == 4)
    got = await otobo_client.get_ticket(ticket_id=tid)
    assert got.title == title + "-updated"
    assert got.priority
    assert (got.priority.name == "4 high" or got.priority.id == 4)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_add_article_domain(otobo_client: OTOBOZnunyClient) -> None:
    title = f"updart-{int(time.time())}"
    created = await otobo_client.create_ticket(
        TicketCreate(
            title=title,
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="init", body="init", content_type="text/plain; charset=utf-8"),
        ),
    )
    tid = created.id
    note_body = "added-note-body"
    updated = await otobo_client.update_ticket(
        TicketUpdate(
            id=tid,
            article=Article(subject="note", body=note_body, content_type="text/plain; charset=utf-8"),
        ),
    )
    assert updated.id == tid
    got = await otobo_client.get_ticket(ticket_id=tid)
    assert any(note_body in (a.body or "") for a in got.get_articles())
