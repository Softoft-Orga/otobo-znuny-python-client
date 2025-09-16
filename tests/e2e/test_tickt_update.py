# tests/test_ticket_update.py
import time
import pytest
from otobo.models.ticket_models import TicketBase, ArticleDetail
from otobo.models.request_models import TicketCreateRequest, TicketUpdateRequest, TicketGetRequest

@pytest.mark.asyncio
async def test_update_title_and_priority(otobo_client):
    title = f"upd-{int(time.time())}"
    created = await otobo_client.create_ticket(
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=title,
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject="init",
                Body="init-body",
                ContentType="text/plain; charset=utf-8",
            ),
        )
    )
    tid = int(created.TicketID)
    updated = await otobo_client.update_ticket(
        TicketUpdateRequest(
            TicketID=tid,
            Ticket=TicketBase(
                Title=title + "-updated",
                Priority="4 high",
            ),
        )
    )
    assert updated.Title == title + "-updated"
    assert updated.Priority in {"4 high", "4"}

    got = await otobo_client.get_ticket(TicketGetRequest(TicketID=tid, AllArticles=1))
    assert got.Title == title + "-updated"
    assert got.Priority in {"4 high", "4"}

@pytest.mark.asyncio
async def test_update_with_numeric_ids(otobo_client):
    title = f"updnum-{int(time.time())}"
    created = await otobo_client.create_ticket(
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=title,
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject="init",
                Body="init",
                ContentType="text/plain; charset=utf-8",
            ),
        )
    )
    tid = int(created.TicketID)
    updated = await otobo_client.update_ticket(
        TicketUpdateRequest(
            TicketID=tid,
            Ticket=TicketBase(
                PriorityID=5,
            ),
        )
    )
    assert str(updated.TicketID) == str(tid)
    assert updated.Priority in {"5 very high", "5"}

    got = await otobo_client.get_ticket(TicketGetRequest(TicketID=tid))
    assert got.Priority in {"5 very high", "5"}

@pytest.mark.asyncio
async def test_update_add_article(otobo_client):
    title = f"updart-{int(time.time())}"
    created = await otobo_client.create_ticket(
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=title,
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject="init",
                Body="init",
                ContentType="text/plain; charset=utf-8",
            ),
        )
    )
    tid = int(created.TicketID)
    note_body = "added-note-body"
    updated = await otobo_client.update_ticket(
        TicketUpdateRequest(
            TicketID=tid,
            Article=ArticleDetail(
                Subject="note",
                Body=note_body,
                ContentType="text/plain; charset=utf-8",
            ),
        )
    )
    assert str(updated.TicketID) == str(tid)

    got = await otobo_client.get_ticket(TicketGetRequest(TicketID=tid, AllArticles=1))
    articles = got.Article if isinstance(got.Article, list) else [got.Article]
    assert any(note_body in a.Body for a in articles if getattr(a, "Body", None))
