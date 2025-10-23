import time

import pytest

from otobo_znuny_python_client.clients.otobo_client import OTOBOZnunyClient
from otobo_znuny_python_client.domain_models.basic_auth_model import BasicAuth
from otobo_znuny_python_client.domain_models.ticket_models import Article, IdName, TicketCreate
from otobo_znuny_python_client.util.otobo_errors import OTOBOError


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_ticket_create_with_restricted_user_should_fail(otobo_client: OTOBOZnunyClient,
                                                              security_user_auth: BasicAuth) -> None:
    title = f"plain-{int(time.time())}"
    try:
        otobo_client.login(security_user_auth)
        await otobo_client.create_ticket(
            TicketCreate(
                title=title,
                queue=IdName(name="Raw"),
                state=IdName(name="new"),
                priority=IdName(name="3 normal"),
                type=IdName(name="Incident"),
                customer_user="customer@localhost.de",
                article=Article(subject="Plain", body="Hello world", content_type="text/plain; charset=utf-8"),
            ),
        )
        pytest.fail("create_ticket should fail")
    except OTOBOError:
        pass
