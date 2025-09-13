import enum
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from .request_models import AuthData


class TicketOperation(Enum):
    """
    Enumeration of supported ticket operations in the OTOBO Webservice API.
    Each member stores both the OTOBO short name and the Type string.
    """
    CREATE = ("TicketCreate", "Ticket::TicketCreate")
    SEARCH = ("TicketSearch", "Ticket::TicketSearch")
    GET = ("TicketGet", "Ticket::TicketGet")
    UPDATE = ("TicketUpdate", "Ticket::TicketUpdate")

    def __new__(cls, name: str, operation_type: str):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.operation_type = operation_type
        return obj

    @property
    def type(self) -> str:
        """Return the OTOBO 'Type' string, e.g. 'Ticket::TicketCreate'."""
        return self.operation_type


class OTOBOClientConfig(BaseModel):
    """
    Configuration model for initializing an OTOBOClient.

    Attributes:
        base_url (str):
            The root URL of the OTOBO installation, e.g.
            `https://server/otobo/nph-genericinterface.pl`.
        service (str):
            The name of the generic interface connector configured in OTOBO.
        auth (AuthData):
            Authentication credentials or tokens required by the Webservice.
        operations (Dict[TicketOperation, str]):
            Mapping from TicketOperation enum members to the corresponding
            endpoint names as configured in OTOBO, for example:
            `{ TicketOperation.CREATE: "ticket-create", ... }`.
    """
    base_url: str = Field(
        ...,
        description="Base URL of the OTOBO installation, e.g. https://server/otobo/nph-genericinterface.pl"
    )
    service: str = Field(
        ...,
        description="Webservice connector name"
    )
    auth: AuthData
    operations: Dict[TicketOperation, str] = Field(
        ...,
        description=(
            "Mapping of operation keys to endpoint names, "
            "e.g. {TicketOperation.CREATE: 'ticket-create', ...}"
        )
    )


from pathlib import Path
from typing import Dict, Any
import yaml
from .request_models import AuthData

TYPE_TO_ENUM = {op.type: op for op in TicketOperation}


def _read_yaml(path: str | Path) -> Dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _extract_operations_by_type(ws: Dict[str, Any]) -> Dict[TicketOperation, str]:
    ops = ws.get("Provider", {}).get("Operation", {}) or {}
    result: Dict[TicketOperation, str] = {}
    for endpoint_name, cfg in ops.items():
        type_str = str((cfg or {}).get("Type", "")).strip()
        enum_key = TYPE_TO_ENUM.get(type_str)
        if enum_key:
            result[enum_key] = str(endpoint_name)
    return result


def create_otobo_client_config(
        webservice_yaml_path: str | Path,
        base_url: str,
        auth: AuthData,
        service: str,
) -> OTOBOClientConfig:
    data = _read_yaml(webservice_yaml_path)
    operations = _extract_operations_by_type(data)
    if not operations:
        raise ValueError("No supported ticket operations found in webservice YAML.")
    return OTOBOClientConfig(
        base_url=base_url,
        service=service,
        auth=auth,
        operations=operations,
    )
