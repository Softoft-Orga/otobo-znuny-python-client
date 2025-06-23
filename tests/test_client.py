from typing import Any, Dict

import httpx
import pytest

from models.client_config_models import TicketOperation, OTOBOClientConfig
from models.request_models import (
    TicketCreateParams, TicketGetParams, TicketUpdateParams,
    TicketSearchParams
)
from models.response_models import (
    OTOBOTicketCreateResponse, OTOBOTicketGetResponse,
    TicketUpdateResponse, TicketSearchResponse, TicketGetResponse
)
from models.ticket_models import TicketDetailOutput, ArticleDetail
from otobo_client import OTOBOClient
from otobo_errors import OTOBOError


# Dummy Async Client to inject
class DummyAsyncClient:
    def __init__(self, response_json: Dict[str, Any], status: int = 200):
        self._response_json = response_json
        self._status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, method: str, url: str, json=None, headers=None):
        class DummyResponse:
            def __init__(self, data, status):
                self._data = data
                self.status_code = status

            def json(self):
                return self._data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise httpx.HTTPStatusError('Error', request=None, response=None)

        return DummyResponse(self._response_json, self._status)


@pytest.fixture
def base_config():
    auth = {
        'UserLogin': 'u', 'Password': 'p'
    }
    return OTOBOClientConfig(
        base_url='http://example.com/otobo',
        service='SVC',
        auth=auth,
        operations={
            TicketOperation.CREATE: 'TicketCreate',
            TicketOperation.GET: 'TicketGet',
            TicketOperation.UPDATE: 'TicketUpdate',
            TicketOperation.SEARCH: 'TicketSearch',
            TicketOperation.HISTORY_GET: 'TicketHistoryGet',
        }
    )


@pytest.mark.asyncio
async def test_create_ticket_success(base_config):
    dummy = DummyAsyncClient(
        OTOBOTicketCreateResponse(
            TicketNumber="2039",
            TicketID=1,
            Ticket=TicketDetailOutput(
                Article=ArticleDetail(),
                DynamicField=[]
            ),
            ArticleID=1)
    )
    client = OTOBOClient(base_config, client=dummy)
    payload = TicketCreateParams(
        Ticket={'Title': 'T', 'Queue': 'Q', 'State': 'new', 'Priority': '3 normal', 'CustomerUser': 'c'},
        Article={'Subject': 's', 'Body': 'b', 'MimeType': 'text/plain'})
    res = await client.create_ticket(payload)
    assert isinstance(res, OTOBOTicketCreateResponse)
    assert res.TicketID == 1


@pytest.mark.asyncio
async def test_get_ticket_success(base_config):
    data = OTOBOTicketGetResponse(
        Ticket=[TicketDetailOutput(TicketID=5, Title='Test Ticket', Article=ArticleDetail(), DynamicField=[])])
    dummy = DummyAsyncClient(data)
    client = OTOBOClient(base_config, client=dummy)
    params = TicketGetParams(TicketID=5)
    res = await client.get_ticket(params)
    assert isinstance(res, TicketGetResponse)
    assert res.Ticket.TicketID == 5


@pytest.mark.asyncio
async def test_update_ticket_success(base_config):
    data = TicketUpdateResponse(TicketID=7, Ticket=TicketDetailOutput(Article=ArticleDetail(), DynamicField=[]))
    dummy = DummyAsyncClient(data)
    client = OTOBOClient(base_config, client=dummy)
    payload = TicketUpdateParams(TicketID=7)
    res = await client.update_ticket(payload)
    assert isinstance(res, TicketUpdateResponse)
    assert res.TicketID == 7


@pytest.mark.asyncio
async def test_search_tickets_success(base_config):
    data = {'TicketID': [10, 11]}
    dummy = DummyAsyncClient(data)
    client = OTOBOClient(base_config, client=dummy)
    query = TicketSearchParams()
    res = await client.search_tickets(query)
    assert isinstance(res, TicketSearchResponse)
    assert res.TicketID == [10, 11]


@pytest.mark.asyncio
async def test_error_response_raises(base_config):
    error = {'Error': {'ErrorCode': 'X', 'ErrorMessage': 'msg'}}
    dummy = DummyAsyncClient(error)
    client = OTOBOClient(base_config, client=dummy)
    with pytest.raises(OTOBOError) as ei:
        await client.create_ticket(
            TicketCreateParams(
                Ticket={'Title': 'T', 'Queue': 'Q', 'State': 'new', 'Priority': '3 normal', 'CustomerUser': 'c'},
                Article={'Subject': 's', 'Body': 'b', 'MimeType': 'text/plain'})
        )
    assert 'X' in str(ei.value)


@pytest.fixture
async def client_with_dummy(base_config):
    # default dummy returns empty dict
    dummy = DummyAsyncClient({})
    return OTOBOClient(base_config, client=dummy)



@pytest.mark.asyncio
async def test_search_tickets_success(base_config):
    response_json = {'TicketID': [10, 11]}
    dummy = DummyAsyncClient(response_json)
    client = OTOBOClient(base_config, client=dummy)
    query = TicketSearchParams()
    res = await client.search_tickets(query)
    assert isinstance(res, TicketSearchResponse)
    assert res.TicketID == [10, 11]




@pytest.mark.asyncio
async def test_operation_not_registered(base_config):
    bad_config = base_config.copy(deep=True)
    bad_config.operations.pop(TicketOperation.CREATE)
    dummy = DummyAsyncClient({'any': 'thing'})
    client = OTOBOClient(bad_config, client=dummy)
    payload = TicketCreateParams(
        Ticket={'Title': 'T', 'Queue': 'Q', 'State': 'new', 'Priority': '3 normal', 'CustomerUser': 'c'},
        Article={'Subject': 's', 'Body': 'b', 'MimeType': 'text/plain'}
    )
    with pytest.raises(RuntimeError):
        await client.create_ticket(payload)


@pytest.mark.asyncio
async def test_error_response_raises(base_config):
    error_json = {'Error': {'ErrorCode': 'X', 'ErrorMessage': 'msg'}}
    dummy = DummyAsyncClient(error_json)
    client = OTOBOClient(base_config, client=dummy)
    with pytest.raises(OTOBOError) as exc:
        await client.create_ticket(
            TicketCreateParams(
                Ticket={'Title': 'T', 'Queue': 'Q', 'State': 'new', 'Priority': '3 normal', 'CustomerUser': 'c'},
                Article={'Subject': 's', 'Body': 'b', 'MimeType': 'text/plain'}
            )
        )
    assert exc.value.code == 'X'
    assert exc.value.message == 'msg'
