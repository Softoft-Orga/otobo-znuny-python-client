import pytest
import httpx
import time

from models.client_config_models import TicketOperation, OTOBOClientConfig
from models.request_models import (
    AuthData,
    TicketCreateParams,
    TicketSearchParams,
    TicketGetParams,
    TicketUpdateParams,
    TicketHistoryParams,
)
from otobo_client import OTOBOClient
from models.response_models import (
    OTOBOTicketCreateResponse,
    OTOBOTicketGetResponse,
    TicketSearchResponse,
    OTOBOTicketHistoryResponse,
    TicketUpdateResponse,
    FullTicketSearchResponse,
)

# Integration tests for async OTOBOClient against real server
BASE_URL = "http://18.193.56.84/otobo/nph-genericinterface.pl"
SERVICE = "OTOBO"
USER = "root@localhost"
PASSWORD = "1234"
OPERATIONS = {
    TicketOperation.CREATE.value: "ticket",
    TicketOperation.SEARCH.value: "ticket/search",
    TicketOperation.GET.value: "ticket/get",
    TicketOperation.UPDATE.value: "ticket",
    TicketOperation.HISTORY_GET.value: "ticket/history",
}

@pytest.fixture(scope="module")
async def async_client():
    client = httpx.AsyncClient()
    yield client
    await client.aclose()

@pytest.fixture(scope="module")
async def client(async_client):
    cfg = OTOBOClientConfig(
        base_url=BASE_URL,
        service=SERVICE,
        auth=AuthData(UserLogin=USER, Password=PASSWORD),
        operations=OPERATIONS,
    )
    return OTOBOClient(cfg, client=async_client)

@pytest.fixture(scope="module")
async def ticket_id(client):
    # create a new ticket
    ts = int(time.time())
    title = f"TestTicket {ts}"
    payload = TicketCreateParams(
        Ticket={
            "Title": title,
            "Queue": "Raw",
            "State": "new",
            "Priority": "3 normal",
            "CustomerUser": USER,
        },
        Article={
            "CommunicationChannel": "Email",
            "Charset": "utf-8",
            "Subject": "Integration Test",
            "Body": "This is a test",
            "MimeType": "text/plain",
        }
    )
    res: OTOBOTicketCreateResponse = await client.create_ticket(payload)
    assert isinstance(res, OTOBOTicketCreateResponse)
    return res.TicketID

@pytest.mark.asyncio
async def test_search_ticket(client, ticket_id):
    query = TicketSearchParams(TicketNumber=str(ticket_id))
    res: TicketSearchResponse = await client.search_tickets(query)
    assert isinstance(res, TicketSearchResponse)
    assert ticket_id in res.TicketID

@pytest.mark.asyncio
async def test_get_ticket(client, ticket_id):
    params = TicketGetParams(TicketID=ticket_id, AllArticles=0, DynamicFields=0)
    res: OTOBOTicketGetResponse = await client.get_ticket(params)
    assert isinstance(res, OTOBOTicketGetResponse)
    assert res.Ticket[0].TicketID == ticket_id

@pytest.mark.asyncio
async def test_update_ticket(client, ticket_id):
    payload = TicketUpdateParams(TicketID=ticket_id, Ticket={"State": "closed successful"})
    res: TicketUpdateResponse = await client.update_ticket(payload)
    assert isinstance(res, TicketUpdateResponse)
    assert res.TicketID == ticket_id

@pytest.mark.asyncio
async def test_get_history(client, ticket_id):
    params = TicketHistoryParams(TicketID=str(ticket_id), AllArticles=0)
    res: OTOBOTicketHistoryResponse = await client.get_ticket_history(params)
    assert isinstance(res, OTOBOTicketHistoryResponse)
    assert any(entry.TicketID == ticket_id for entry in res.History)

@pytest.mark.asyncio
async def test_search_and_get(client, ticket_id):
    query = TicketSearchParams(TicketNumber=str(ticket_id))
    full: FullTicketSearchResponse = await client.search_and_get(query)
    assert isinstance(full, FullTicketSearchResponse)
    # full is List[List[TicketDetail]]
    results = [detail for sub in full for detail in sub]
    assert any(d.TicketID == ticket_id for d in results)
