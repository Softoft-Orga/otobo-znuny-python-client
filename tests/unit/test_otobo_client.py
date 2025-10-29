from typing import Any

import pytest
from pydantic import SecretStr

from otobo_znuny_python_client.clients import otobo_client
from otobo_znuny_python_client.clients.otobo_client import OTOBOZnunyClient
from otobo_znuny_python_client.domain_models.basic_auth_model import BasicAuth
from otobo_znuny_python_client.domain_models.otobo_client_config import ClientConfig
from otobo_znuny_python_client.domain_models.ticket_models import IdName, TicketCreate, TicketSearch
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.models.response_models import (
    WsTicketGetResponse,
    WsTicketResponse,
    WsTicketSearchResponse,
)
from otobo_znuny_python_client.models.ticket_models import WsTicketOutput


def make_client(*, async_client: Any = None) -> OTOBOZnunyClient:
    config = ClientConfig(
        base_url="https://example.org/api",
        webservice_name="Service",
        operation_url_map={
            TicketOperation.CREATE: "ticket-create",
            TicketOperation.SEARCH: "ticket-search",
            TicketOperation.GET: "ticket-get",
            TicketOperation.UPDATE: "ticket-update",
        },
    )
    client = OTOBOZnunyClient(config=config, client=async_client)
    auth = BasicAuth(user_login="user", password=SecretStr("pass"))
    client.login(auth)
    return client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_ticket_uses_mappers(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyRequest:
        def model_dump(self, *, exclude_none: bool, by_alias: bool) -> dict[str, Any]:
            assert exclude_none is True
            assert by_alias is True
            return {"ticket_data": "value"}

    def fake_build_request(arg: TicketCreate) -> DummyRequest:
        assert arg.title == "Example"
        return DummyRequest()

    monkeypatch.setattr(
        otobo_client,
        "to_ws_ticket_create",
        fake_build_request,
    )

    async def fake_send(*args, **kwargs):  # type: ignore[no-untyped-def]
        return WsTicketResponse(Ticket=WsTicketOutput(TicketID=123, TicketNumber="2025123"))

    def fake_parse(arg: Any) -> Any:
        return TicketCreate(
            title="Parsed",
            queue=IdName(name="Queue"),
            state=IdName(name="open"),
            priority=IdName(name="normal"),
            customer_user="user@example.com",
        )

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "_send", fake_send)
    monkeypatch.setattr(
        otobo_client,
        "from_ws_ticket_detail",
        fake_parse,
    )

    client = make_client()
    ticket_in = TicketCreate(
        title="Example",
        queue=IdName(name="Q"),
        state=IdName(name="open"),
        priority=IdName(name="normal"),
        customer_user="user@example.com",
    )

    result = await client.create_ticket(ticket_in)

    assert result.title == "Parsed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_ticket_raises_when_missing_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        otobo_client,
        "to_ws_ticket_create",
        lambda arg: type("Req", (), {"model_dump": lambda *a, **kw: {}})(),
    )

    async def fake_send(*args, **kwargs):  # type: ignore[no-untyped-def]
        return WsTicketResponse()

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "_send", fake_send)

    client = make_client()
    ticket_in = TicketCreate(
        title="Test",
        queue=IdName(name="Q"),
        state=IdName(name="open"),
        priority=IdName(name="normal"),
        customer_user="user@example.com",
    )

    with pytest.raises(RuntimeError, match="create returned no Ticket"):
        await client.create_ticket(ticket_in)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ticket_returns_parsed_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyRequest:
        def model_dump(self, *, exclude_none: bool, by_alias: bool) -> dict[str, Any]:
            assert exclude_none is True
            assert by_alias is True
            return {"TicketID": "123"}

    async def fake_send(*args, **kwargs):  # type: ignore[no-untyped-def]
        return WsTicketGetResponse(Ticket=[WsTicketOutput(TicketID=456, TicketNumber="2025456")])

    def fake_parse(arg: Any) -> Any:
        return TicketCreate(
            title="ParsedTitle",
            queue=IdName(name="Q"),
            state=IdName(name="open"),
            priority=IdName(name="normal"),
            customer_user="user@example.com",
        )

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "_send", fake_send)
    monkeypatch.setattr(otobo_client, "from_ws_ticket_detail", fake_parse)

    client = make_client()
    result = await client.get_ticket(ticket_id=456)

    assert result.title == "ParsedTitle"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ticket_raises_when_not_single_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_send(*args, **kwargs):  # type: ignore[no-untyped-def]
        return WsTicketGetResponse(Ticket=[WsTicketOutput(TicketID=1), WsTicketOutput(TicketID=2)])

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "_send", fake_send)

    client = make_client()

    with pytest.raises(RuntimeError, match="expected exactly one ticket"):
        await client.get_ticket(ticket_id=123)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_tickets_returns_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyRequest:
        def model_dump(self, *, exclude_none: bool, by_alias: bool) -> dict[str, Any]:
            return {"StateType": "open"}

    monkeypatch.setattr(
        otobo_client,
        "to_ws_ticket_search",
        lambda arg: DummyRequest(),
    )

    async def fake_send(*args, **kwargs):  # type: ignore[no-untyped-def]
        return WsTicketSearchResponse(TicketID=[10, 20, 30])

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "_send", fake_send)

    client = make_client()
    search_criteria = TicketSearch()
    result = await client.search_tickets(search_criteria)

    assert result == [10, 20, 30]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_tickets_handles_missing_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        otobo_client,
        "to_ws_ticket_search",
        lambda arg: type("Req", (), {"model_dump": lambda *a, **kw: {}})(),
    )

    async def fake_send(*args, **kwargs):  # type: ignore[no-untyped-def]
        return WsTicketSearchResponse()

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "_send", fake_send)

    client = make_client()
    result = await client.search_tickets(TicketSearch())

    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_and_get_calls_get_for_each_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    get_calls = []

    async def fake_search(self, ticket_search: TicketSearch) -> list[int]:  # type: ignore[no-untyped-def]
        return [1, 2, 3]

    async def fake_get(self, ticket_id: int | str) -> TicketCreate:  # type: ignore[no-untyped-def]
        get_calls.append(ticket_id)
        return TicketCreate(
            title=f"Ticket {ticket_id}",
            queue=IdName(name="Q"),
            state=IdName(name="open"),
            priority=IdName(name="normal"),
            customer_user="user@example.com",
        )

    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "search_tickets", fake_search)
    monkeypatch.setattr(otobo_client.OTOBOZnunyClient, "get_ticket", fake_get)

    client = make_client()
    results = await client.search_and_get(TicketSearch())

    assert len(results) == 3
    assert get_calls == [1, 2, 3]
    assert results[0].title == "Ticket 1"
