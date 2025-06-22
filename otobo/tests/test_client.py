import pytest
import requests
from otobo.otobo_client import (
    OTOBOClient,
    OperationResult
)
from client_config_models import TicketOperation, OTOBOClientConfig
from models.request_models import AuthData, TicketSearchParams, TicketCreateParams, TicketHistoryParams, TicketUpdateParams

# dummy JSON payloads for each operation
DUMMY_RESPONSES = {
    'ticket-search': {"TicketID": [101, 102]},
    'ticket-get':    {"TicketID": 101, "Title": "Test"},
    'ticket-create': {"TicketID": 201, "ArticleID": 301},
    'ticket-update': {"TicketID": 101, "ArticleID": 302},
    'ticket-history-get': {"TicketHistoryModel": [{"Change": "x"}]},
}

class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
    def json(self):
        return self._data
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    def fake_request(method, url, params=None, json=None, headers=None):
        # choose endpoint by last path segment
        endpoint = url.rstrip('/').split('/')[-1]
        data = DUMMY_RESPONSES.get(endpoint)
        if data is not None:
            return DummyResponse(data)
        return DummyResponse({}, status=404)
    monkeypatch.setattr(requests, "request", fake_request)

@pytest.fixture
def client():
    auth = AuthData(UserLogin="root@localhost", Password="1234")
    cfg = OTOBOClientConfig(
        base_url="https://demo.otobo.org/otobo/nph-genericinterface.pl",
        service="MyService",
        auth=auth,
        operations={
            TicketOperation.SEARCH.value: "ticket-search",
            TicketOperation.GET.value: "ticket-get",
            TicketOperation.CREATE.value: "ticket-create",
            TicketOperation.UPDATE.value: "ticket-update",
            TicketOperation.HISTORY_GET.value: "ticket-history-get",
        }
    )
    return OTOBOClient(cfg)

def test_search_tickets(client):
    params = TicketSearchParams(Title="foo")
    ids = client.search_tickets(params)
    assert ids == [101, 102]

def test_get_ticket(client):
    result = client.get_ticket(101, DynamicFields=1)
    assert isinstance(result, OperationResult)
    assert result["TicketID"] == 101
    assert result["Title"] == "Test"

def test_create_ticket(client):
    payload = TicketCreateParams(
        Ticket={"Title": "New"},
        Article={"Subject": "Subj", "Body": "Body", "MimeType": "text/plain"}
    )
    result = client.create_ticket(payload)
    assert result.Success == 1
    assert result["TicketID"] == 201

def test_update_ticket(client):
    payload = TicketUpdateParams(
        TicketID=101,
        Ticket={"State": "closed"}
    )
    result = client.update_ticket(payload)
    assert result["TicketID"] == 101
    assert result["ArticleID"] == 302

def test_get_ticket_history(client):
    payload = TicketHistoryParams(TicketID="101")
    result = client.get_ticket_history(payload)
    assert result["TicketHistoryModel"] == [{"Change": "x"}]

def test_search_and_get(client):
    params = TicketSearchParams(Title="bar")
    combined = client.search_and_get(params, DynamicFields=0)
    assert isinstance(combined, list)
    assert combined[0]["TicketID"] == 101

def test_missing_operation_raises():
    auth = AuthData(UserLogin="u", Password="p")
    cfg = OTOBOClientConfig(
        base_url="https://x",
        service="S",
        auth=auth,
        operations={"TicketGet": "ticket-get"}  # missing search
    )
    client = OTOBOClient(cfg)
    with pytest.raises(RuntimeError):
        client.search_tickets(TicketSearchParams())

    with pytest.raises(RuntimeError):
        client.create_ticket(TicketCreateParams(
            Ticket={"A":1}, Article={"Subject":"s","Body":"b","MimeType":"text/plain"}
        ))
    # get should work
    # monkeypatch HTTP separately if needed
    # history should raise
    with pytest.raises(RuntimeError):
        client.get_ticket_history(TicketHistoryParams(TicketID="1"))
