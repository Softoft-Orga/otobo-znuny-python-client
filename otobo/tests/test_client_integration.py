import logging

import pytest
from _pytest.fixtures import fixture

from otobo.otobo_client import (
    OTOBOClient
)
from client_config_models import OTOBOClientConfig
from models.request_models import AuthData, TicketSearchParams, TicketCreateParams, TicketHistoryParams, TicketUpdateParams
import time

# Integration tests hitting real OTOBO server
BASE_URL = "http://18.193.56.84/otobo/nph-genericinterface.pl"
SERVICE = "OTOBO"
USER = "root@localhost"
PASSWORD = "1234"


logging.basicConfig(level=logging.DEBUG)

@pytest.fixture(scope="module")
def client():
    auth = AuthData(UserLogin=USER, Password=PASSWORD)
    config = OTOBOClientConfig(
        base_url=BASE_URL,
        service=SERVICE,
        auth=auth,
        operations={
            "TicketCreate": "ticket-create",
            "TicketSearch": "ticket-search",
            "TicketGet": "ticket-get",
            "TicketUpdate": "ticket-update",
            "TicketHistoryGet": "ticket-history-get",
        }
    )
    return OTOBOClient(config)

@fixture(autouse=True)
def ticket(client):
    """
    Fixture to ensure we have a clean ticket state before each test.
    This will create a new ticket and store its ID for later tests.
    """
    ts = int(time.time())
    title = f"TestTicket {ts}"
    payload = TicketCreateParams(
        Ticket={
            "Title": title,
            "Queue": "Raw",
            "State": "new",
            "Priority": "3 normal",
            "CustomerUser": "customer@localhost.de",
        },
        Article={
            "CommunicationChannel": "Email",
            "Charset": 'utf-8',
            "Subject": "Integration Test",
            "Body": "This is a test",
            "MimeType": "text/plain"
        }
    )
    res = client.create_ticket(payload)
    assert res.Success == 1, f"Create failed: {res.ErrorMessage}"
    assert "TicketID" in res.Data
    yield res.Data["TicketID"]

@pytest.mark.order(1)
def test_create_ticket(client):
    ts = int(time.time())
    title = f"TestTicket {ts}"
    payload = TicketCreateParams(
        Ticket={
            "Title": title,
            "Queue": "Raw",
            "State": "new",
            "Priority": "3 normal",
            "CustomerUser": "customer@localhost.de",
        },
        Article={
            "Subject": "Integration Test",
            "Body": "This is a test",
            "MimeType": "text/plain"
        }
    )
    res = client.create_ticket(payload)
    assert res.Success == 1, f"Create failed: {res.ErrorMessage}"
    assert "TicketID" in res.Data
    # store for later tests
    pytest.ticket_id = res.Data["TicketID"]

@pytest.mark.order(2)
def test_search_ticket(client):
    ts = pytest.ticket_id
    # search by TicketNumber substring
    query = TicketSearchParams(TicketNumber=str(ts))
    ids = client.search_tickets(query)
    assert ts in ids

@pytest.mark.order(3)
def test_get_ticket(client):
    ts = pytest.ticket_id
    res = client.get_ticket(ts, AllArticles=0, DynamicFields=0)
    assert res.Success == 1
    assert res.Data.get("TicketID") == ts

@pytest.mark.order(4)
def test_update_ticket(client):
    ts = pytest.ticket_id
    payload = TicketUpdateParams(
        TicketID=ts,
        Ticket={"State": "closed"}
    )
    res = client.update_ticket(payload)
    assert res.Success == 1
    assert res.Data.get("TicketID") == ts

@pytest.mark.order(5)
def test_get_history(client):
    ts = pytest.ticket_id
    payload = TicketHistoryParams(TicketID=str(ts), AllArticles=0)
    res = client.get_ticket_history(payload)
    assert res.Success == 1
    assert isinstance(res.Data.get("TicketHistoryModel"), list)

@pytest.mark.order(6)
def test_search_and_get(client):
    ts = pytest.ticket_id
    query = TicketSearchParams(TicketNumber=str(ts))
    results = client.search_and_get(query, AllArticles=0)
    assert isinstance(results, list)
    # first result should match
    assert results[0].get("TicketID") == ts
