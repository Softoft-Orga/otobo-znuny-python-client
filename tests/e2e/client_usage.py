import time
import logging
from textwrap import dedent

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


@pytest.mark.asyncio
async def test_ticket_creation_edge_cases(otobo_client):
    ts = int(time.time())
    base_prefix = f"edge-{ts}"

    base_ticket_kwargs: dict[str, str] = {
        "Queue": "Raw",
        "State": "new",
        "Priority": "3 normal",
        "Type": "Incident",
        "CustomerUser": "customer@localhost.de",
    }
    base_expected_fields: dict[str, str] = {
        "Queue": "Raw",
        "State": "new",
        "Priority": "3 normal",
        "Type": "Incident",
        "CustomerUserID": "customer@localhost.de",
    }

    cases = [
        {
            "title": f"{base_prefix}-plain",
            "article": ArticleDetail(
                Subject="Plain text article",
                Body="Edge case base body",
                ContentType="text/plain; charset=utf-8",
            ),
            "article_expected": {"body_contains": "Edge case base body"},
        },
        {
            "title": f"{base_prefix}-unicode",
            "article": ArticleDetail(
                Subject="Unicode article",
                Body=dedent(
                    """\
                    Hello team,
                    this body includes emojis 😊 and german umlauts äöüß.
                    Best regards,
                    Integration Test
                    """
                ),
                ContentType="text/plain; charset=utf-8",
            ),
            "article_expected": {"body_contains": "emoji 😊"},
        },
        {
            "title": f"{base_prefix}-html",
            "ticket_overrides": {"Priority": "4 high"},
            "article": ArticleDetail(
                Subject="HTML article",
                Body=dedent(
                    """\
                    <p><strong>Edge Case</strong> ticket body with HTML content &amp; special chars like &lt;test&gt;.</p>
                    <ul><li>Line 1</li><li>Line 2</li></ul>
                    """
                ),
                ContentType="text/html; charset=utf-8",
            ),
            "article_expected": {"body_contains": "special chars like <test>"},
            "expected": {"Priority": "4 high"},
        },
        {
            "title": f"{base_prefix}-numeric",
            "ticket_overrides": {
                "QueueID": 2,
                "StateID": 1,
                "PriorityID": 5,
                "TypeID": 2,
            },
            "unset_fields": ["Queue", "State", "Priority", "Type"],
            "article": ArticleDetail(
                Subject="Numeric identifiers",
                Body="Ticket created via numeric identifiers for queue/state/priority/type",
                ContentType="text/plain; charset=utf-8",
            ),
            "expected": {
                "Queue": "Raw",
                "State": "new",
                "Priority": "5 very high",
                "Type": "Incident",
            },
        },
        {
            "title": (f"{base_prefix}-long-" + "x" * 200)[:240],
            "article": ArticleDetail(
                Subject="Long title article",
                Body="Ticket verifying that extremely long titles are accepted and stored.",
                ContentType="text/plain; charset=utf-8",
            ),
            "title_exact": False,
            "min_title_length": 100,
        },
        {
            "title": f"{base_prefix}-iso",
            "ticket_overrides": {"CustomerID": "EdgeCorp"},
            "article": ArticleDetail(
                Subject="ISO charset",
                Body="Body with latin1 characters äöüß stored with ISO charset.",
                ContentType="text/plain; charset=iso-8859-1",
            ),
            "article_expected": {
                "content_type": "text/plain; charset=iso-8859-1",
                "body_contains": "äöüß",
            },
            "expected_customer_id": "EdgeCorp",
        },
    ]

    created_ticket_ids: list[int] = []

    for case in cases:
        ticket_kwargs = base_ticket_kwargs.copy()
        ticket_kwargs.update(case.get("ticket_overrides", {}))
        for field in case.get("unset_fields", []):
            ticket_kwargs.pop(field, None)
        ticket_kwargs["Title"] = case["title"]

        create_request = TicketCreateRequest(
            Ticket=TicketBase(**ticket_kwargs),
            Article=case["article"],
        )

        logger.info("Creating edge case ticket %s", case["title"])
        created_ticket = await otobo_client.create_ticket(create_request)
        ticket_id = int(created_ticket.TicketID)
        assert ticket_id > 0
        created_ticket_ids.append(ticket_id)

        fetched_ticket = await otobo_client.get_ticket(
            TicketGetRequest(TicketID=ticket_id, AllArticles=1)
        )

        if case.get("title_exact", True):
            assert fetched_ticket.Title == ticket_kwargs["Title"]
        else:
            expected_prefix = case.get(
                "expected_title_prefix", ticket_kwargs["Title"][:50]
            )
            assert fetched_ticket.Title.startswith(expected_prefix)
        if "min_title_length" in case:
            assert len(fetched_ticket.Title) >= case["min_title_length"]

        expected_fields = base_expected_fields.copy()
        expected_fields.update(case.get("expected", {}))
        for field, expected_value in expected_fields.items():
            assert getattr(fetched_ticket, field) == expected_value

        if "expected_customer_id" in case:
            assert fetched_ticket.CustomerID == case["expected_customer_id"]

        articles = (
            fetched_ticket.Article
            if isinstance(fetched_ticket.Article, list)
            else [fetched_ticket.Article]
        )
        assert articles
        primary_article = articles[0]

        article_checks = case.get("article_expected", {})
        if "content_type" in article_checks:
            assert primary_article.ContentType == article_checks["content_type"]
        if "body_contains" in article_checks:
            assert article_checks["body_contains"] in primary_article.Body

    assert len(created_ticket_ids) == len(set(created_ticket_ids))
