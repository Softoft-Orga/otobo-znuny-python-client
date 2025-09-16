import asyncio
import random
import time
import logging
import pytest

from otobo import (
    TicketSearchRequest,
    TicketGetRequest,
    TicketUpdateRequest,
    TicketCreateRequest,
)
from otobo.models.ticket_models import TicketBase, ArticleDetail

logger = logging.getLogger("e2e_test")


async def _create_basic_ticket(otobo_client, title: str) -> tuple[int, str]:
    create_req = TicketCreateRequest(
        Ticket=TicketBase(
            Title=title,
            Queue="Raw",
            State="new",
            Priority="3 normal",
            Type="Incident",
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="Integration Test",
            Body="pytest body",
            ContentType="text/plain; charset=utf-8",
        ),
    )
    ticket = await otobo_client.create_ticket(create_req)
    ticket_id = int(ticket.TicketID)
    ticket_number = ticket.TicketNumber
    assert ticket_number is not None
    return ticket_id, ticket_number


async def _wait_for_ticket_ids(
    otobo_client,
    query: TicketSearchRequest,
    expected_ids: list[int],
    attempts: int = 6,
    delay: float = 1.0,
) -> list[int]:
    expected_set = set(expected_ids)
    for attempt in range(attempts):
        current_ids = await otobo_client.search_tickets(query)
        filtered = [int(tid) for tid in current_ids if int(tid) in expected_set]
        if set(filtered) == expected_set and len(filtered) == len(expected_ids):
            logger.info("Found expected ticket ids on attempt %s: %s", attempt + 1, filtered)
            return filtered
        logger.info(
            "Waiting for ticket ids. Attempt %s/%s. Expected=%s, got=%s",
            attempt + 1,
            attempts,
            expected_ids,
            current_ids,
        )
        await asyncio.sleep(delay)
    raise AssertionError(
        f"Search results did not return expected ticket ids after {attempts} attempts"
    )


@pytest.mark.asyncio
async def test_ticket_flow(otobo_client):
    ts = int(time.time())
    title = f"pytest-{ts}"

    # 1. create
    create_req = TicketCreateRequest(
        Ticket=TicketBase(
            Title=title,
            Queue="Raw",
            State="new",
            Priority="3 normal",
            Type="Incident",
            CustomerUser="customer@localhost.de",
        ),
        Article=ArticleDetail(
            Subject="Integration Test",
            Body="pytest body",
            ContentType="text/plain; charset=utf-8",
        ),
    )
    create_res = await otobo_client.create_ticket(create_req)
    ticket_id = int(create_res.TicketID)
    ticket_number = create_res.TicketNumber
    assert ticket_id > 0
    assert ticket_number

    # 2. search
    search_res = await otobo_client.search_tickets(
        TicketSearchRequest(Queues=["Raw"])
    )
    assert ticket_id in search_res

    # 3. get
    get_res = await otobo_client.get_ticket(
        TicketGetRequest(TicketID=ticket_id, AllArticles=1)
    )
    assert get_res

    # 4. update
    update_res = await otobo_client.update_ticket(
        TicketUpdateRequest(
            TicketID=ticket_id,
            Ticket=TicketBase(Queue="Junk"),
        )
    )
    assert update_res.TicketID == str(ticket_id)

    # 5. search_and_get
    combined = await otobo_client.search_and_get(
        TicketSearchRequest(Queues=["Raw"])
    )
    assert isinstance(combined, list)


async def test_search_and_get_multiple_cases(otobo_client):
    ts = int(time.time())
    titles = [f"pytest-batch-{ts}-{i}" for i in range(3)]

    created = [await _create_basic_ticket(otobo_client, title) for title in titles]
    ticket_ids = [ticket_id for ticket_id, _ in created]
    ticket_numbers = [ticket_number for _, ticket_number in created]

    search_query = TicketSearchRequest(TicketNumber=ticket_numbers)
    search_ids = await _wait_for_ticket_ids(otobo_client, search_query, ticket_ids)

    assert set(search_ids) == set(ticket_ids)

    # Case 1: Fetch all matching tickets (max_tickets larger than available)
    full_details = await otobo_client.search_and_get(search_query, max_tickets=5)
    full_ids = [int(ticket.TicketID) for ticket in full_details]
    assert full_ids == search_ids

    # Case 2: Respect max_tickets limit
    limited_details = await otobo_client.search_and_get(search_query, max_tickets=2)
    limited_ids = [int(ticket.TicketID) for ticket in limited_details]
    assert limited_ids == search_ids[:2]

    # Case 3: Shuffle order deterministically when requested
    random_state = random.getstate()
    try:
        random.seed(0)
        shuffled_details = await otobo_client.search_and_get(
            search_query, max_tickets=3, shuffle=True
        )
        shuffled_ids = [int(ticket.TicketID) for ticket in shuffled_details]

        random.seed(0)
        expected_shuffled = search_ids.copy()
        random.shuffle(expected_shuffled)
        expected_shuffled = expected_shuffled[:3]

        assert shuffled_ids == expected_shuffled
    finally:
        random.setstate(random_state)

async def test_multiple_ticket_updates(otobo_client):
    ts = int(time.time())

    base_ticket_kwargs = dict(
        Queue="Raw",
        State="new",
        Priority="3 normal",
        Type="Incident",
        CustomerUser="customer@localhost.de",
    )

    update_scenarios = [
        {"field": "Queue", "value": "Junk", "update_kwargs": {"Queue": "Junk"}},
        {
            "field": "State",
            "value": "closed successful",
            "update_kwargs": {"State": "closed successful"},
        },
        {
            "field": "Priority",
            "value": "4 high",
            "update_kwargs": {"Priority": "4 high"},
        },
    ]

    created_tickets: list[dict[str, object]] = []

    for index, scenario in enumerate(update_scenarios, start=1):
        title = f"pytest-update-{index}-{ts}"
        create_req = TicketCreateRequest(
            Ticket=TicketBase(Title=title, **base_ticket_kwargs),
            Article=ArticleDetail(
                Subject=f"Integration Test {index}",
                Body="pytest body",
                ContentType="text/plain; charset=utf-8",
            ),
        )

        created_ticket = await otobo_client.create_ticket(create_req)
        ticket_id = int(created_ticket.TicketID)
        assert ticket_id > 0
        assert created_ticket.TicketNumber

        created_tickets.append(
            {
                "ticket_id": ticket_id,
                "ticket_number": created_ticket.TicketNumber,
                "title": title,
                "scenario": scenario,
            }
        )

    for ticket in created_tickets:
        scenario = ticket["scenario"]
        update_req = TicketUpdateRequest(
            TicketID=ticket["ticket_id"],
            Ticket=TicketBase(**scenario["update_kwargs"]),
        )

        updated_ticket = await otobo_client.update_ticket(update_req)
        assert int(updated_ticket.TicketID) == ticket["ticket_id"]
        assert updated_ticket.TicketNumber == ticket["ticket_number"]
        assert getattr(updated_ticket, scenario["field"]) == scenario["value"]

        fetched_ticket = await otobo_client.get_ticket(
            TicketGetRequest(TicketID=ticket["ticket_id"], AllArticles=1)
        )
        assert fetched_ticket.TicketNumber == ticket["ticket_number"]
        assert fetched_ticket.Title == ticket["title"]
        assert getattr(fetched_ticket, scenario["field"]) == scenario["value"]
