import json
import sys
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from http import HTTPMethod

# Ensure the package uses its expected import layout
sys.path.append(str(Path(__file__).resolve().parents[2] / "src/otobo"))

from client.otobo_client import OTOBOClient
from models.client_config_models import OTOBOClientConfig, TicketOperation
from models.request_models import (
    AuthData,
    TicketCreateRequest,
    TicketGetRequest,
    TicketSearchRequest,
    TicketUpdateRequest,
)
from models.response_models import TicketGetResponse, TicketResponse, TicketSearchResponse
from models.ticket_models import TicketDetailOutput
from util.otobo_errors import OTOBOError


@pytest.fixture
def sample_config() -> OTOBOClientConfig:
    return OTOBOClientConfig(
        base_url="https://example.com/otobo/",
        service="AIService",
        auth=AuthData(UserLogin="user", Password="pass"),
        operations={
            TicketOperation.CREATE: "ticket-create",
            TicketOperation.GET: "ticket-get",
            TicketOperation.UPDATE: "ticket-update",
            TicketOperation.SEARCH: "ticket-search",
        },
    )


@pytest_asyncio.fixture
async def client(sample_config: OTOBOClientConfig):
    oc = OTOBOClient(sample_config)
    try:
        yield oc
    finally:
        await oc._client.aclose()


@pytest.mark.asyncio
async def test_build_url(client: OTOBOClient, sample_config: OTOBOClientConfig):
    url = client._build_url("endpoint")
    assert url == "https://example.com/otobo/Webservice/AIService/endpoint"


@pytest.mark.asyncio
async def test_check_operation_registered_passes(client: OTOBOClient):
    client._check_operation_registered(TicketOperation.CREATE)
    client._check_operation_registered([TicketOperation.CREATE, TicketOperation.GET])


@pytest.mark.asyncio
async def test_check_operation_registered_single_missing(sample_config: OTOBOClientConfig):
    cfg = sample_config.model_copy(deep=True)
    cfg.operations.pop(TicketOperation.GET)
    client = OTOBOClient(cfg)
    with pytest.raises(RuntimeError):
        client._check_operation_registered(TicketOperation.GET)


@pytest.mark.asyncio
async def test_check_operation_registered_multiple_missing(sample_config: OTOBOClientConfig):
    cfg = sample_config.model_copy(deep=True)
    cfg.operations.pop(TicketOperation.UPDATE)
    client = OTOBOClient(cfg)
    with pytest.raises(RuntimeError):
        client._check_operation_registered([TicketOperation.CREATE, TicketOperation.UPDATE])


@pytest.mark.asyncio
async def test_check_response_handles_error(client: OTOBOClient):
    response = httpx.Response(
        200,
        json={"Error": {"ErrorCode": "E", "ErrorMessage": "fail"}},
        request=httpx.Request("GET", "http://x"),
    )
    with pytest.raises(OTOBOError):
        client._check_response(response)


@pytest.mark.asyncio
async def test_check_response_raises_http_error(client: OTOBOClient):
    response = httpx.Response(
        404,
        json={},
        request=httpx.Request("GET", "http://x"),
    )
    with pytest.raises(httpx.HTTPStatusError):
        client._check_response(response)


@pytest.mark.asyncio
async def test_check_response_ok(client: OTOBOClient):
    response = httpx.Response(200, json={}, request=httpx.Request("GET", "http://x"))
    client._check_response(response)


@pytest.mark.asyncio
async def test_request_makes_call_and_returns_model(sample_config: OTOBOClientConfig):
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["method"] = request.method
        recorded["url"] = str(request.url)
        recorded["json"] = json.loads(request.content)
        return httpx.Response(200, json={"TicketID": [42]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OTOBOClient(sample_config, http_client)
        result = await client._request(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            TicketSearchResponse,
            data={"Extra": "field"},
        )
    assert recorded["method"] == "POST"
    assert recorded["url"] == "https://example.com/otobo/Webservice/AIService/ticket-search"
    assert recorded["json"] == {"UserLogin": "user", "Password": "pass", "Extra": "field"}
    assert isinstance(result, TicketSearchResponse)
    assert result.TicketID == [42]


@pytest.mark.asyncio
async def test_request_returns_unvalidated_on_error(sample_config: OTOBOClientConfig):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"TicketID": ["bad"]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OTOBOClient(sample_config, http_client)
        result = await client._request(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            TicketSearchResponse,
        )
    assert result.TicketID == ["bad"]


@pytest.mark.asyncio
async def test_request_raises_when_operation_missing(sample_config: OTOBOClientConfig):
    cfg = sample_config.model_copy(deep=True)
    cfg.operations.pop(TicketOperation.SEARCH)
    client = OTOBOClient(cfg)
    try:
        with pytest.raises(RuntimeError):
            await client._request(
                HTTPMethod.POST,
                TicketOperation.SEARCH,
                TicketSearchResponse,
            )
    finally:
        await client._client.aclose()


@pytest.mark.asyncio
async def test_create_ticket_uses_request_and_returns_ticket(client: OTOBOClient, monkeypatch):
    ticket = TicketDetailOutput(TicketID=1, Article=[], DynamicField=[])
    payload = TicketCreateRequest()

    async def fake_request(self, http_method, op, response_model, data=None):
        assert op == TicketOperation.CREATE
        assert data == payload.model_dump(exclude_none=True)
        return TicketResponse(Ticket=ticket)

    monkeypatch.setattr(OTOBOClient, "_request", fake_request)
    result = await client.create_ticket(payload)
    assert result == ticket


@pytest.mark.asyncio
async def test_get_ticket_returns_ticket(client: OTOBOClient, monkeypatch):
    ticket = TicketDetailOutput(TicketID=1, Article=[], DynamicField=[])

    async def fake_request(self, http_method, op, response_model, data=None):
        assert op == TicketOperation.GET
        return TicketGetResponse(Ticket=[ticket])

    monkeypatch.setattr(OTOBOClient, "_request", fake_request)
    result = await client.get_ticket(TicketGetRequest(TicketID=1))
    assert result == ticket


@pytest.mark.asyncio
async def test_get_ticket_raises_when_multiple(client: OTOBOClient, monkeypatch):
    t1 = TicketDetailOutput(TicketID=1, Article=[], DynamicField=[])
    t2 = TicketDetailOutput(TicketID=2, Article=[], DynamicField=[])

    async def fake_request(self, http_method, op, response_model, data=None):
        return TicketGetResponse(Ticket=[t1, t2])

    monkeypatch.setattr(OTOBOClient, "_request", fake_request)
    with pytest.raises(AssertionError):
        await client.get_ticket(TicketGetRequest(TicketID=1))


@pytest.mark.asyncio
async def test_update_ticket_returns_ticket(client: OTOBOClient, monkeypatch):
    ticket = TicketDetailOutput(TicketID=1, Article=[], DynamicField=[])
    payload = TicketUpdateRequest(TicketID=1)

    async def fake_request(self, http_method, op, response_model, data=None):
        assert op == TicketOperation.UPDATE
        assert data == payload.model_dump(exclude_none=True)
        return TicketResponse(Ticket=ticket)

    monkeypatch.setattr(OTOBOClient, "_request", fake_request)
    result = await client.update_ticket(payload)
    assert result == ticket


@pytest.mark.asyncio
async def test_update_ticket_raises_when_no_ticket(client: OTOBOClient, monkeypatch):
    payload = TicketUpdateRequest(TicketID=1)

    async def fake_request(self, http_method, op, response_model, data=None):
        return TicketResponse(Ticket=None)

    monkeypatch.setattr(OTOBOClient, "_request", fake_request)
    with pytest.raises(RuntimeError):
        await client.update_ticket(payload)


@pytest.mark.asyncio
async def test_search_tickets_returns_ids(client: OTOBOClient, monkeypatch):
    class Response:
        def __init__(self):
            self.TicketID = [1, 2, 3]
            self.TicketIDs = [1, 2, 3]

    async def fake_request(self, http_method, op, response_model, data=None):
        assert op == TicketOperation.SEARCH
        return Response()

    monkeypatch.setattr(OTOBOClient, "_request", fake_request)
    result = await client.search_tickets(TicketSearchRequest())
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_search_and_get_combines_results(client: OTOBOClient, monkeypatch):
    t1 = TicketDetailOutput(TicketID=1, Article=[], DynamicField=[])
    t2 = TicketDetailOutput(TicketID=2, Article=[], DynamicField=[])

    async def fake_search(query):
        return [1, 2]

    async def fake_get(req):
        return t1 if req.TicketID == 1 else t2

    monkeypatch.setattr(client, "search_tickets", fake_search)
    monkeypatch.setattr(client, "get_ticket", fake_get)

    result = await client.search_and_get(TicketSearchRequest())
    assert result == [t1, t2]


@pytest.mark.asyncio
async def test_search_and_get_raises_when_operation_missing(sample_config: OTOBOClientConfig):
    cfg = sample_config.model_copy(deep=True)
    cfg.operations.pop(TicketOperation.GET)
    client = OTOBOClient(cfg)
    try:
        with pytest.raises(RuntimeError):
            await client.search_and_get(TicketSearchRequest())
    finally:
        await client._client.aclose()
