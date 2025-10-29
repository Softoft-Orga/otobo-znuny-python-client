"""Convenience re-exports for the public package API."""

from .clients.otobo_client import OTOBOZnunyClient as Client
from .clients.otobo_client import OTOBOZnunyClient
from .domain_models.basic_auth_model import BasicAuth
from .domain_models.otobo_client_config import ClientConfig, OperationUrlMap
from .domain_models.ticket_models import (
    Article,
    DynamicFieldFilter,
    IdName,
    Ticket,
    TicketBase,
    TicketCreate,
    TicketSearch,
    TicketUpdate,
)
from .domain_models.ticket_operation import TicketOperation
from .setup.webservices.builder import WebserviceBuilder
from .setup.webservices.operations import (
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
)
from .setup.webservices.webservice_models import OperationSpec
from .cli.interface import (
    ArgsBuilder,
    CmdResult,
    OtoboCommandRunner,
    OtoboConsole,
    OTOBO_COMMANDS,
    Permission,
)

__all__ = [
    "Article",
    "ArgsBuilder",
    "BasicAuth",
    "Client",
    "ClientConfig",
    "CmdResult",
    "DynamicFieldFilter",
    "IdName",
    "OperationSpec",
    "OperationUrlMap",
    "OtoboCommandRunner",
    "OtoboConsole",
    "OTOBO_COMMANDS",
    "OTOBOZnunyClient",
    "Permission",
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
