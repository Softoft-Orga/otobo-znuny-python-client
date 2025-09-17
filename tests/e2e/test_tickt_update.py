# tests/test_ticket_update.py
import time
import pytest

from domain_models.ticket_models import Ticket, IdName, Article


@pytest.mark.asyncio
async def test_update_title_and_priority(otobo_client):
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
async def test_update_with_numeric_ids(otobo_client):
    title = f"updnum-{int(time.time())}"
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
    updated = await otobo_client.update_ticket(
        Ticket(
            id=tid,
            priority=IdName(id=5),
        )
    )
    assert updated.id == tid
    assert updated.priority and (updated.priority.id == 5 or updated.priority.name in {"5 very high", "5"})
    got = await otobo_client.get_ticket(ticket_id=tid)
    assert got.priority and (got.priority.id == 5 or got.priority.name in {"5 very high", "5"})

@pytest.mark.asyncio
async def test_update_add_article(otobo_client):
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
