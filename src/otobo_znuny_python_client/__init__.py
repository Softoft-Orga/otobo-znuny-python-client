"""Convenience re-exports for the public package API."""

from otobo_znuny.cli.otobo_console import OtoboConsole
from otobo_znuny.setup.webservices import (
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
)
from otobo_znuny.setup.webservices.builder import WebserviceBuilder
from .clients.otobo_client import OTOBOZnunyClient
from .clients.otobo_client import OTOBOZnunyClient as Client
from .domain_models.basic_auth_model import BasicAuth
from .domain_models.otobo_client_config import ClientConfig, OperationUrlMap
from .domain_models.ticket_models import (
    Article,
    IdName,
    Ticket,
    TicketBase,
    TicketCreate,
    TicketSearch,
    TicketUpdate,
)
from .domain_models.ticket_operation import TicketOperation

__all__ = [
    "Article",
    "BasicAuth",
    "Client",
    "ClientConfig",
    "IdName",
    "OperationUrlMap",
    "OtoboConsole",
    "OTOBOZnunyClient",
    "SUPPORTED_OPERATION_SPECS",
    "SUPPORTED_OPERATIONS_DOC",
    "Ticket",
    "TicketBase",
    "TicketCreate",
    "TicketOperation",
    "TicketSearch",
    "TicketUpdate",
    "WebserviceBuilder",
]
