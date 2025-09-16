# tests/test_ticket_search.py
import time
from textwrap import dedent
import pytest

from otobo.models.ticket_models import TicketBase, ArticleDetail
from otobo.models.request_models import TicketCreateRequest, TicketSearchRequest, TicketGetRequest

@pytest.mark.asyncio
async def test_search_returns_ids_for_created_tickets(otobo_client):
    prefix = f"search-{int(time.time())}"
    reqs = [
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=f"{prefix}-a",
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject="A",
                Body="alpha",
                ContentType="text/plain; charset=utf-8",
            ),
        ),
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=f"{prefix}-b",
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject="B",
                Body=dedent("""\
                    body-b
                """),
                ContentType="text/plain; charset=utf-8",
            ),
        ),
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=f"{prefix}-c",
                Queue="Raw",
                State="new",
                Priority="4 high",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject="C",
                Body="charlie",
                ContentType="text/plain; charset=utf-8",
            ),
        ),
    ]
    created = [await otobo_client.create_ticket(r) for r in reqs]
    created_ids = {int(t.TicketID) for t in created}
    assert all(i > 0 for i in created_ids)

    search_req = TicketSearchRequest(Title=[f"{prefix}-a", f"{prefix}-b", f"{prefix}-c"])
    found_ids = set(await otobo_client.search_tickets(search_req))
    assert created_ids.issubset(found_ids)

@pytest.mark.asyncio
async def test_search_and_get_returns_full_tickets(otobo_client):
    prefix = f"searchget-{int(time.time())}"
    r1 = TicketCreateRequest(
        Ticket=TicketBase(
            Title=f"{prefix}-x",
            Queue="Raw",
            State="new",
            Priority="3 normal",
            Type="Incident",
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="X",
            Body="x-body",
            ContentType="text/plain; charset=utf-8",
        ),
    )
    r2 = TicketCreateRequest(
        Ticket=TicketBase(
            Title=f"{prefix}-y",
            Queue="Raw",
            State="new",
            Priority="3 normal",
            Type="Incident",
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="Y",
            Body="y-body",
            ContentType="text/plain; charset=utf-8",
        ),
    )
    t1 = await otobo_client.create_ticket(r1)
    t2 = await otobo_client.create_ticket(r2)
    ids = {int(t1.TicketID), int(t2.TicketID)}
    assert all(i > 0 for i in ids)

    search_req = TicketSearchRequest(Title=[f"{prefix}-x", f"{prefix}-y"])
    tickets = await otobo_client.search_and_get(search_req, max_tickets=5, shuffle=False)
    numbers = {t.TicketNumber for t in tickets}
    assert len(tickets) >= 2
    got_ids = set()
    for t in tickets:
        assert t.Title in {f"{prefix}-x", f"{prefix}-y"}
        assert t.Queue in {"Raw", None} or isinstance(t.Queue, str)
        arts = t.Article if isinstance(t.Article, list) else [t.Article]
        assert arts and isinstance(arts[0].Body, str)
        got_detail = await otobo_client.get_ticket(TicketGetRequest(TicketID=int(t.TicketID), AllArticles=1))
        assert got_detail.TicketNumber in numbers
        got_ids.add(int(t.TicketID))
    assert ids.issubset(got_ids)

@pytest.mark.asyncio
async def test_search_no_results(otobo_client):
    search_req = TicketSearchRequest(Title=[f"no-such-title-{int(time.time())}"])
    ids = await otobo_client.search_tickets(search_req)
    assert ids == []
    details = await otobo_client.search_and_get(search_req, max_tickets=3)
    assert details == []
