# tests/test_ticket_search.py
import time

import pytest

from otobo_znuny.clients.otobo_client import OTOBOZnunyClient
from otobo_znuny.domain_models.ticket_models import Article, IdName, TicketCreate, TicketSearch


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_search_returns_ids_for_created_tickets(otobo_client: OTOBOZnunyClient) -> None:
    prefix = f"search-{int(time.time())}"
    t1 = await otobo_client.create_ticket(
        TicketCreate(
            title=f"{prefix}-a",
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="A", body="alpha", content_type="text/plain; charset=utf-8"),
        ),
    )
    t2 = await otobo_client.create_ticket(
        TicketCreate(
            title=f"{prefix}-b",
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="B", body="bravo", content_type="text/plain; charset=utf-8"),
        ),
    )
    t3 = await otobo_client.create_ticket(
        TicketCreate(
            title=f"{prefix}-c",
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="4 high"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="C", body="charlie", content_type="text/plain; charset=utf-8"),
        ),
    )
    created_ids = {t1.id, t2.id, t3.id}
    assert all(i is not None and i > 0 for i in created_ids)

    search = TicketSearch(
        titles=[f"{prefix}-a", f"{prefix}-b", f"{prefix}-c"],
        queues=[IdName(name="Raw")],
        use_subqueues=False,
        limit=50,
    )
    found_ids = set(await otobo_client.search_tickets(search))
    assert created_ids.issubset(found_ids)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_search_and_get_returns_full_tickets(otobo_client: OTOBOZnunyClient) -> None:
    prefix = f"searchget-{int(time.time())}"
    await otobo_client.create_ticket(
        TicketCreate(
            title=f"{prefix}-x",
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="X", body="x-body", content_type="text/plain; charset=utf-8"),
        ),
    )
    await otobo_client.create_ticket(
        TicketCreate(
            title=f"{prefix}-y",
            queue=IdName(name="Raw"),
            state=IdName(name="new"),
            priority=IdName(name="3 normal"),
            type=IdName(name="Incident"),
            customer_user="customer@localhost.de",
            article=Article(subject="Y", body="y-body", content_type="text/plain; charset=utf-8"),
        ),
    )

    search = TicketSearch(
        titles=[f"{prefix}-x", f"{prefix}-y"],
        queues=[IdName(name="Raw")],
        use_subqueues=False,
        limit=10,
    )
    tickets = await otobo_client.search_and_get(search)
    assert len(tickets) >= 2
    titles = {t.title for t in tickets}
    assert {f"{prefix}-x", f"{prefix}-y"}.issubset(titles)
    assert all(t.queue and isinstance(t.queue.name, str) for t in tickets)
    for t in tickets:
        assert t.articles
        assert isinstance(t.get_articles()[0].body, str)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_search_no_results(otobo_client: OTOBOZnunyClient) -> None:
    search = TicketSearch(titles=[f"no-such-title-{int(time.time())}"])
    ids = await otobo_client.search_tickets(search)
    assert ids == []
    details = await otobo_client.search_and_get(search)
    assert details == []
