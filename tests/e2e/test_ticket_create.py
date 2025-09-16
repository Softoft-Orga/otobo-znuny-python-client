# tests/test_ticket_create_basic.py
import time
from textwrap import dedent
import pytest

from otobo.models.ticket_models import ArticleDetail, TicketBase
from otobo.models.request_models import TicketCreateRequest, TicketGetRequest

@pytest.mark.asyncio
async def test_ticket_create_and_get_plain(otobo_client):
    title = f"plain-{int(time.time())}"
    req = TicketCreateRequest(
        Ticket=TicketBase(
            Title=title,
            Queue="Raw",
            State="new",
            Priority="3 normal",
            Type="Incident",
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="Plain",
            Body="Hello world",
            ContentType="text/plain; charset=utf-8",
        ),
    )
    created = await otobo_client.create_ticket(req)
    tid = int(created.TicketID)
    assert tid > 0

    got = await otobo_client.get_ticket(TicketGetRequest(TicketID=tid, AllArticles=1))
    assert got.Title == title
    assert got.Queue == "Raw"
    assert got.State == "new"
    assert got.Priority == "3 normal"
    assert got.Type == "Incident"
    arts = got.Article if isinstance(got.Article, list) else [got.Article]
    assert arts and "Hello world" in arts[0].Body

@pytest.mark.asyncio
async def test_ticket_create_and_get_html(otobo_client):
    title = f"html-{int(time.time())}"
    html_body = dedent(
        """\
        <p><strong>Edge</strong> with HTML &amp; chars &lt;x&gt;.</p>
        """
    )
    req = TicketCreateRequest(
        Ticket=TicketBase(
            Title=title,
            Queue="Raw",
            State="new",
            Priority="4 high",
            Type="Incident",
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="HTML",
            Body=html_body,
            ContentType="text/html; charset=utf-8",
        ),
    )
    created = await otobo_client.create_ticket(req)
    tid = int(created.TicketID)
    assert tid > 0

    got = await otobo_client.get_ticket(TicketGetRequest(TicketID=tid, AllArticles=1))
    assert got.Title == title
    assert got.Priority == "4 high"
    arts = got.Article if isinstance(got.Article, list) else [got.Article]
    assert arts and "<x>" in arts[0].Body

@pytest.mark.asyncio
async def test_ticket_create_with_numeric_ids(otobo_client):
    title = f"numeric-{int(time.time())}"
    req = TicketCreateRequest(
        Ticket=TicketBase(
            Title=title,
            QueueID=2,
            StateID=1,
            PriorityID=5,
            TypeID=2,
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="Numeric IDs",
            Body="Created using numeric identifiers",
            ContentType="text/plain; charset=utf-8",
        ),
    )
    created = await otobo_client.create_ticket(req)
    tid = int(created.TicketID)
    assert tid > 0

    got = await otobo_client.get_ticket(TicketGetRequest(TicketID=tid, AllArticles=1))
    assert got.Title == title
    assert got.Queue in ("Raw", "2")
    assert got.State in ("new", "1")
    assert got.Priority in ("5 very high", "5")
    assert got.Type in ("Incident", "2")
