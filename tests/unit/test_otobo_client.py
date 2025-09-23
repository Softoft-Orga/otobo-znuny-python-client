import json
from http import HTTPMethod
from typing import Any
from unittest.mock import AsyncMock, call

import pytest

from otobo.clients import otobo_client
from otobo.clients.otobo_client import OTOBOZnunyClient
from otobo.domain_models.basic_auth_model import BasicAuth
from otobo.domain_models.otobo_client_config import OTOBOClientConfig
from otobo.domain_models.ticket_models import TicketCreate, TicketSearch
from otobo.domain_models.ticket_operation import TicketOperation
from otobo.models.response_models import (
    TicketGetResponse,
    TicketResponse,
    TicketSearchResponse,
)
from otobo.models.ticket_models import TicketDetailOutput
from otobo.util.otobo_errors import OTOBOError


class DummyResponse:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        if 400 <= self.status_code:
            raise RuntimeError(f"status {self.status_code}")


def make_client(async_client: AsyncMock | None = None) -> OTOBOZnunyClient:
    config = OTOBOClientConfig(
        base_url="https://example.org/api/",
        webservice_name="Service",
        auth=BasicAuth(UserLogin="user", Password="pass"),
        operation_url_map={
            TicketOperation.CREATE: "ticket-create",
            TicketOperation.SEARCH: "ticket-search",
            TicketOperation.GET: "ticket-get",
            TicketOperation.UPDATE: "ticket-update",
        },
    )
    return OTOBOZnunyClient(config=config, client=async_client)


@pytest.mark.asyncio
async def test_send_combines_auth_with_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    http_client = AsyncMock()
    payload = {"Ticket": {"Title": "Example"}}
    http_client.request.return_value = DummyResponse(payload)
    client = make_client(async_client=http_client)

    result = await client._send(  # type: ignore[attr-defined]
        HTTPMethod.POST,
        TicketOperation.CREATE,
        TicketResponse,
        data={"Extra": "Value"},
    )

    http_client.request.assert_awaited_once()
    args, kwargs = http_client.request.call_args
    assert args == ("POST", "https://example.org/api/Webservice/Service/ticket-create")
    assert kwargs["json"] == {
        "UserLogin": "user",
        "Password": "pass",
        "Extra": "Value",
    }
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert isinstance(result, TicketResponse)
    assert result.Ticket is not None
    assert result.Ticket.Title == "Example"


@pytest.mark.asyncio
async def test_send_raises_otobo_error_when_error_in_payload() -> None:
    http_client = AsyncMock()
    http_client.request.return_value = DummyResponse(
        {"Error": {"ErrorCode": "500", "ErrorMessage": "boom"}}
    )
    client = make_client(async_client=http_client)

    with pytest.raises(OTOBOError) as exc:
        await client._send(  # type: ignore[attr-defined]
            HTTPMethod.POST,
            TicketOperation.CREATE,
            TicketResponse,
            data={},
        )
    assert exc.value.code == "500"
    assert exc.value.message == "boom"


@pytest.mark.asyncio
async def test_send_falls_back_to_model_construct_on_validation_error() -> None:
    http_client = AsyncMock()
    http_client.request.return_value = DummyResponse({"value": "not-an-int"})
    client = make_client(async_client=http_client)

    class DummyModel(otobo_client.BaseModel):  # type: ignore[attr-defined]
        value: int

    result = await client._send(  # type: ignore[attr-defined]
        HTTPMethod.POST,
        TicketOperation.CREATE,
        DummyModel,
        data={},
    )

    assert isinstance(result, DummyModel)
    assert result.value == "not-an-int"


@pytest.mark.asyncio
async def test_create_ticket_uses_mappers(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())
    ticket = TicketCreate()
    request_dump = {"Ticket": "payload"}
    captured: dict[str, Any] = {}

    class DummyRequest:
        def model_dump(self, *, exclude_none: bool, by_alias: bool) -> dict[str, Any]:
            captured["dump_args"] = (exclude_none, by_alias)
            return request_dump

    def fake_build_request(arg: TicketCreate) -> DummyRequest:
        captured["request_arg"] = arg
        return DummyRequest()

    monkeypatch.setattr(
        otobo_client,
        "build_ticket_create_request",
        fake_build_request,
    )
    response_ticket = TicketDetailOutput(TicketID=1)

    async def fake_send(method, operation, response_model, data=None):  # type: ignore[no-untyped-def]
        captured["send_args"] = (method, operation, response_model, data)
        return TicketResponse(Ticket=response_ticket)

    monkeypatch.setattr(client, "_send", fake_send)

    parsed_ticket = object()
    def fake_parse(arg: Any) -> Any:
        captured["parsed_arg"] = arg
        return parsed_ticket

    monkeypatch.setattr(
        otobo_client,
        "parse_ticket_detail_output",
        fake_parse,
    )

    result = await client.create_ticket(ticket)

    assert result is parsed_ticket
    assert captured["request_arg"] is ticket
    assert captured["dump_args"] == (True, True)
    method, operation, response_model, data = captured["send_args"]
    assert method == HTTPMethod.POST
    assert operation == TicketOperation.CREATE
    assert response_model is TicketResponse
    assert data == request_dump
    assert captured["parsed_arg"] is response_ticket


@pytest.mark.asyncio
async def test_create_ticket_raises_when_missing_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())

    monkeypatch.setattr(
        otobo_client,
        "build_ticket_create_request",
        lambda _: type("DummyRequest", (), {"model_dump": lambda self, **_: {}})(),
    )

    async def fake_send(method, operation, response_model, data=None):  # type: ignore[no-untyped-def]
        return TicketResponse(Ticket=None)

    monkeypatch.setattr(client, "_send", fake_send)

    with pytest.raises(RuntimeError):
        await client.create_ticket(TicketCreate())


@pytest.mark.asyncio
async def test_get_ticket_returns_parsed_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())
    request_dump = {"TicketID": 42}

    class DummyRequest:
        def model_dump(self, *, exclude_none: bool, by_alias: bool) -> dict[str, Any]:
            return request_dump

    monkeypatch.setattr(
        otobo_client,
        "build_ticket_get_request",
        lambda ticket_id: DummyRequest(),
    )

    response_payload = {"TicketID": 42}

    async def fake_send(method, operation, response_model, data=None):  # type: ignore[no-untyped-def]
        assert data == request_dump
        return TicketGetResponse(Ticket=[response_payload])

    monkeypatch.setattr(client, "_send", fake_send)

    parsed_ticket = object()
    captured: dict[str, Any] = {}

    def fake_parse(arg: Any) -> Any:
        captured["arg"] = arg
        return parsed_ticket

    monkeypatch.setattr(
        otobo_client,
        "parse_ticket_detail_output",
        fake_parse,
    )

    result = await client.get_ticket(42)
    assert result is parsed_ticket
    assert "arg" in captured


@pytest.mark.asyncio
async def test_get_ticket_raises_when_not_single_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())

    monkeypatch.setattr(
        otobo_client,
        "build_ticket_get_request",
        lambda _: type("DummyRequest", (), {"model_dump": lambda self, **_: {}})(),
    )

    async def fake_send(method, operation, response_model, data=None):  # type: ignore[no-untyped-def]
        return TicketGetResponse(Ticket=[])

    monkeypatch.setattr(client, "_send", fake_send)

    with pytest.raises(RuntimeError):
        await client.get_ticket(7)


@pytest.mark.asyncio
async def test_search_tickets_returns_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())
    request_dump = {"Title": ["demo"]}

    class DummyRequest:
        def model_dump(self, *, exclude_none: bool, by_alias: bool) -> dict[str, Any]:
            return request_dump

    monkeypatch.setattr(
        otobo_client,
        "build_ticket_search_request",
        lambda _: DummyRequest(),
    )

    async def fake_send(method, operation, response_model, data=None):  # type: ignore[no-untyped-def]
        assert data == request_dump
        return TicketSearchResponse(TicketID=[1, 2, 3])

    monkeypatch.setattr(client, "_send", fake_send)

    result = await client.search_tickets(TicketSearch())
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_search_tickets_handles_missing_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())

    monkeypatch.setattr(
        otobo_client,
        "build_ticket_search_request",
        lambda _: type("DummyRequest", (), {"model_dump": lambda self, **_: {}})(),
    )

    async def fake_send(method, operation, response_model, data=None):  # type: ignore[no-untyped-def]
        return TicketSearchResponse(TicketID=None)

    monkeypatch.setattr(client, "_send", fake_send)

    result = await client.search_tickets(TicketSearch())
    assert result == []


@pytest.mark.asyncio
async def test_search_and_get_calls_get_for_each_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client(async_client=AsyncMock())
    search = TicketSearch()

    async def fake_search(_: TicketSearch) -> list[int]:
        return [11, 22]

    client.search_tickets = AsyncMock(side_effect=fake_search)
    client.get_ticket = AsyncMock(side_effect=[object(), object()])

    result = await client.search_and_get(search)

    assert len(result) == 2
    client.search_tickets.assert_awaited_once_with(search)
    client.get_ticket.assert_has_awaits([call(11), call(22)])
