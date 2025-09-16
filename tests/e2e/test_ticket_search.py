import time

import pytest

from otobo import TicketCreateRequest, TicketSearchRequest
from otobo.models.ticket_models import ArticleDetail, TicketBase


@pytest.mark.asyncio
async def test_searches_through_created_tickets(otobo_client):
    base_ts = int(time.time())
    tickets_to_create = [
        TicketCreateRequest(
            Ticket=TicketBase(
                Title=f"search-ticket-{base_ts}-{index}",
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                Subject=f"Search Test Article {index}",
                Body="pytest body",
                ContentType="text/plain; charset=utf-8",
            ),
        )
        for index in range(3)
    ]

    created_ticket_ids: list[int] = []
    for ticket_request in tickets_to_create:
        ticket_response = await otobo_client.create_ticket(ticket_request)
        created_ticket_ids.append(int(ticket_response.TicketID))

    titles = [
        request.Ticket.Title
        for request in tickets_to_create
        if request.Ticket is not None and request.Ticket.Title is not None
    ]

    search_query = TicketSearchRequest(Title=titles, Queues=["Raw"])
    search_result_ids = await otobo_client.search_tickets(search_query)

    assert search_result_ids, "Expected search to return ticket IDs"
    for ticket_id in created_ticket_ids:
        assert (
            ticket_id in search_result_ids
        ), f"Created ticket id {ticket_id} not found in search results"

    detailed_tickets = await otobo_client.search_and_get(
        search_query, max_tickets=len(titles)
    )

    detailed_ticket_ids = {ticket.TicketID for ticket in detailed_tickets}
    assert set(created_ticket_ids).issubset(
        detailed_ticket_ids
    ), "Detailed search results missing created tickets"

    detailed_titles = {ticket.Title for ticket in detailed_tickets}
    assert set(titles).issubset(
        detailed_titles
    ), "Detailed search results missing expected titles"
