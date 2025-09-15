import time
import logging
import pytest

from otobo import (
    TicketOperation,
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
