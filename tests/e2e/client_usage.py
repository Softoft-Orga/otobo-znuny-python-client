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


@pytest.mark.asyncio
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
