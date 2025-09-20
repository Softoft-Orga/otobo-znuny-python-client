import time

import pytest

from otobo.domain_models.ticket_models import TicketCreate, IdName, Article
from otobo.clients.otobo_client import OTOBOZnunyClient
from otobo.util.otobo_errors import OTOBOError


@pytest.mark.asyncio
async def test_ticket_create_with_restricted_user_should_fail(security_user_client: OTOBOZnunyClient) -> None:
    title = f"plain-{int(time.time())}"
    try:
        await security_user_client.create_ticket(
            TicketCreate(
                title=title,
                queue=IdName(name="Raw"),
                state=IdName(name="new"),
                priority=IdName(name="3 normal"),
                type=IdName(name="Incident"),
                customer_user="customer@localhost.de",
                article=Article(subject="Plain", body="Hello world", content_type="text/plain; charset=utf-8"),
            )
        )
        pytest.fail("create_ticket should fail")
    except OTOBOError as e:
        pass
