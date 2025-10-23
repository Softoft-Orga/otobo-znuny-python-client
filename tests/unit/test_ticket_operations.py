"""Unit tests for complete ticket operations (create, get, update, search)."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from otobo_znuny.clients.otobo_client import OTOBOZnunyClient
from otobo_znuny.domain_models.basic_auth_model import BasicAuth
from otobo_znuny.domain_models.otobo_client_config import ClientConfig
from otobo_znuny.domain_models.ticket_models import (
    Article,
    IdName,
    TicketCreate,
    TicketSearch,
    TicketUpdate,
)
from otobo_znuny.domain_models.ticket_operation import TicketOperation


@pytest.fixture
def client_config() -> ClientConfig:
    """Create a test client configuration."""
    return ClientConfig(
        base_url="https://test.example.com/api/",
        webservice_name="TestService",
        operation_url_map={
            TicketOperation.CREATE: "ticket-create",
            TicketOperation.SEARCH: "ticket-search",
            TicketOperation.GET: "ticket-get",
            TicketOperation.UPDATE: "ticket-update",
        },
    )


@pytest.fixture
def auth() -> BasicAuth:
    """Create test authentication."""
    return BasicAuth(user_login="testuser", password="testpass")


@pytest.fixture
def client(client_config: ClientConfig, auth: BasicAuth) -> OTOBOZnunyClient:
    """Create a test client with mocked HTTP client."""
    http_client = AsyncMock()
    client = OTOBOZnunyClient(config=client_config, client=http_client)
    client.login(auth)
    return client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_ticket_complete_flow(client: OTOBOZnunyClient) -> None:
    """Test creating a ticket with all fields."""
    # Mock HTTP response
    response_data = {
        "Ticket": {
            "TicketID": "123",
            "TicketNumber": "2025010212300001",
            "Title": "Test Ticket",
            "Queue": "Raw",
            "QueueID": "2",
            "State": "new",
            "StateID": "1",
            "Priority": "3 normal",
            "PriorityID": "3",
            "Type": "Incident",
            "TypeID": "1",
            "CustomerUserID": "customer@test.com",
        },
    }

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    # Create ticket
    ticket = TicketCreate(
        title="Test Ticket",
        queue=IdName(name="Raw"),
        state=IdName(name="new"),
        priority=IdName(name="3 normal"),
        type=IdName(name="Incident"),
        customer_user="customer@test.com",
        article=Article(
            subject="Test Subject",
            body="Test Body",
            content_type="text/plain; charset=utf-8",
        ),
    )

    result = await client.create_ticket(ticket)

    assert result.id == 123
    assert result.number == "2025010212300001"
    assert result.title == "Test Ticket"
    assert result.queue
    assert result.queue.name == "Raw"
    assert result.state
    assert result.state.name == "new"
    assert result.priority
    assert result.priority.name == "3 normal"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ticket_by_id(client: OTOBOZnunyClient) -> None:
    """Test retrieving a ticket by ID."""
    # Mock HTTP response
    response_data = {
        "Ticket": [
            {
                "TicketID": "456",
                "TicketNumber": "2025010212300002",
                "Title": "Retrieved Ticket",
                "Queue": "Support",
                "QueueID": "3",
                "State": "open",
                "StateID": "4",
                "Priority": "4 high",
                "PriorityID": "4",
            },
        ],
    }

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    result = await client.get_ticket(456)

    assert result.id == 456
    assert result.title == "Retrieved Ticket"
    assert result.queue
    assert result.queue.name == "Support"
    assert result.priority
    assert result.priority.name == "4 high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_ticket_title_and_priority(client: OTOBOZnunyClient) -> None:
    """Test updating a ticket's title and priority."""
    # Mock HTTP response
    response_data = {
        "Ticket": {
            "TicketID": "789",
            "Title": "Updated Title",
            "Priority": "5 very high",
            "PriorityID": "5",
        },
    }

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    update = TicketUpdate(
        id=789,
        title="Updated Title",
        priority=IdName(name="5 very high"),
    )

    result = await client.update_ticket(update)

    assert result.id == 789
    assert result.title == "Updated Title"
    assert result.priority
    assert result.priority.name == "5 very high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_ticket_with_article(client: OTOBOZnunyClient) -> None:
    """Test updating a ticket and adding an article (note)."""
    # Mock HTTP response
    response_data = {
        "Ticket": {
            "TicketID": "999",
            "Article": [
                {
                    "Subject": "Note",
                    "Body": "This is a note",
                    "ContentType": "text/plain; charset=utf-8",
                },
            ],
        },
    }

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    update = TicketUpdate(
        id=999,
        article=Article(
            subject="Note",
            body="This is a note",
            content_type="text/plain; charset=utf-8",
        ),
    )

    result = await client.update_ticket(update)

    assert result.id == 999
    assert len(result.articles) > 0
    assert "This is a note" in (result.articles[0].body or "")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_tickets_returns_ids(client: OTOBOZnunyClient) -> None:
    """Test searching tickets and getting IDs."""
    # Mock HTTP response
    response_data = {"TicketID": [1, 2, 3, 4, 5]}

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    search = TicketSearch(
        queues=[IdName(name="Raw")],
        states=[IdName(name="new")],
    )

    result = await client.search_tickets(search)

    assert result == [1, 2, 3, 4, 5]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_tickets_no_results(client: OTOBOZnunyClient) -> None:
    """Test searching tickets with no results."""
    # Mock HTTP response
    response_data = {"TicketID": None}

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    search = TicketSearch(titles=["NonExistentTicket12345"])

    result = await client.search_tickets(search)

    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_and_get_tickets(client: OTOBOZnunyClient) -> None:
    """Test searching and retrieving full ticket details."""
    # Mock responses
    search_data = {"TicketID": [10, 20]}
    get_data_1 = {
        "Ticket": [
            {
                "TicketID": "10",
                "Title": "Ticket 10",
                "Queue": "Raw",
                "State": "new",
            },
        ],
    }
    get_data_2 = {
        "Ticket": [
            {
                "TicketID": "20",
                "Title": "Ticket 20",
                "Queue": "Support",
                "State": "open",
            },
        ],
    }

    search_response = AsyncMock()
    search_response.json = lambda: search_data
    search_response.text = "{}"
    search_response.status_code = 200

    get_response_1 = AsyncMock()
    get_response_1.json = lambda: get_data_1
    get_response_1.text = "{}"
    get_response_1.status_code = 200

    get_response_2 = AsyncMock()
    get_response_2.json = lambda: get_data_2
    get_response_2.text = "{}"
    get_response_2.status_code = 200

    client._client.request = AsyncMock(  # type: ignore
        side_effect=[search_response, get_response_1, get_response_2],
    )

    search = TicketSearch(queues=[IdName(name="Raw")])
    results = await client.search_and_get(search)

    assert len(results) == 2
    assert results[0].id == 10
    assert results[0].title == "Ticket 10"
    assert results[1].id == 20
    assert results[1].title == "Ticket 20"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_ticket_with_numeric_ids(client: OTOBOZnunyClient) -> None:
    """Test creating a ticket using numeric IDs instead of names."""
    # Mock HTTP response
    response_data = {
        "Ticket": {
            "TicketID": "555",
            "QueueID": "2",
            "StateID": "1",
            "PriorityID": "4",
            "TypeID": "1",
        },
    }

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    ticket = TicketCreate(
        title="Numeric ID Ticket",
        queue=IdName(id=2),
        state=IdName(id=1),
        priority=IdName(id=4),
        type=IdName(id=1),
        customer_user="customer@test.com",
        article=Article(
            subject="Test",
            body="Test",
            content_type="text/plain; charset=utf-8",
        ),
    )

    result = await client.create_ticket(ticket)

    assert result.id == 555
    assert result.queue
    assert result.queue.id == 2
    assert result.priority
    assert result.priority.id == 4


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_ticket_with_numeric_priority(client: OTOBOZnunyClient) -> None:
    """Test updating a ticket priority using numeric ID."""
    # Mock HTTP response
    response_data = {
        "Ticket": {
            "TicketID": "666",
            "PriorityID": "5",
            "Priority": "5 very high",
        },
    }

    mock_response = AsyncMock()
    mock_response.json = lambda: response_data
    mock_response.text = "{}"
    mock_response.status_code = 200
    client._client.request = AsyncMock(return_value=mock_response)  # type: ignore

    update = TicketUpdate(
        id=666,
        priority=IdName(id=5),
    )

    result = await client.update_ticket(update)

    assert result.id == 666
    assert result.priority
    assert result.priority.id == 5
