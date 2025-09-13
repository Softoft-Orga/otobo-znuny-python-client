import pytest
from pathlib import Path
import textwrap
from typing import Dict

from otobo.models.request_models import AuthData
from otobo.util.webservice_config import create_otobo_client_config
from otobo.models.client_config_models import OTOBOClientConfig, TicketOperation


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    return p

def test_create_otobo_client_config_parses_operations(tmp_path: Path):
    ws = _write(
        tmp_path,
        "ws.yml",
        """
        ---
        Debugger:
          DebugThreshold: debug
          TestMode: '0'
        Description: x
        FrameworkVersion: 7.1.7
        Provider:
          Operation:
            ticket-create:
              Type: Ticket::TicketCreate
            ticket-get:
              Type: Ticket::TicketGet
            ticket-search:
              Type: Ticket::TicketSearch
            ticket-update:
              Type: Ticket::TicketUpdate
          Transport:
            Type: HTTP::REST
        RemoteSystem: ''
        Requester:
          Transport:
            Type: ''
        """,
    )
    auth = AuthData.model_construct()
    cfg = create_otobo_client_config(
        webservice_yaml_path=ws,
        base_url="https://server/otobo/nph-genericinterface.pl",
        auth=auth,
        service="AIService",
    )
    assert isinstance(cfg, OTOBOClientConfig)
    assert cfg.base_url == "https://server/otobo/nph-genericinterface.pl"
    assert cfg.service == "AIService"
    assert cfg.auth is auth
    expected: Dict[TicketOperation, str] = {
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.GET: "ticket-get",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.UPDATE: "ticket-update",
    }
    assert cfg.operations == expected

def test_raises_when_no_supported_operations(tmp_path: Path):
    ws = _write(
        tmp_path,
        "ws_empty.yml",
        """
        ---
        Debugger:
          DebugThreshold: debug
          TestMode: '0'
        Description: x
        FrameworkVersion: 7.1.7
        Provider:
          Operation:
            custom-op:
              Type: Ticket::UnknownThing
          Transport:
            Type: HTTP::REST
        RemoteSystem: ''
        Requester:
          Transport:
            Type: ''
        """,
    )
    auth = AuthData.model_construct()
    with pytest.raises(ValueError):
        create_otobo_client_config(
            webservice_yaml_path=ws,
            base_url="https://server/otobo/nph-genericinterface.pl",
            auth=auth,
            service="AIService",
        )
