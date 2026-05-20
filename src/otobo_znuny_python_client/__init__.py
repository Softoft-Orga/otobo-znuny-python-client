"""Deprecated compatibility package. Prefer `from otobo import OTOBOClient` or `from znuny import ZnunyClient`."""

from otobo import OTOBOClient as OTOBOZnunyClient
from otobo import OTOBOClient as Client
from otobo import (
    Article,
    BasicAuth,
    ClientConfig,
    IdName,
    OperationUrlMap,
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
    Ticket,
    TicketBase,
    TicketCreate,
    TicketOperation,
    TicketSearch,
    TicketUpdate,
    WebserviceBuilder,
)
from otobo_znuny.cli.otobo_console import OtoboConsole
from otobo_znuny.cli.otobo_command_runner import OtoboCommandRunner

__all__ = [
    "Article",
    "BasicAuth",
    "Client",
    "ClientConfig",
    "IdName",
    "OperationUrlMap",
    "OtoboCommandRunner",
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
