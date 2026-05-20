"""Shared OTRS GenericInterface core for OTOBO and Znuny Python SDKs."""

from otrs_gi_core.clients.generic_interface_client import GenericInterfaceClient
from otrs_gi_core.cli.command_runner import ConsoleCommandRunner
from otrs_gi_core.cli.system_console import SystemConsole
from otrs_gi_core.domain_models.basic_auth_model import BasicAuth
from otrs_gi_core.domain_models.client_config import ClientConfig, OperationUrlMap
from otrs_gi_core.domain_models.ticket_models import (
    Article,
    IdName,
    Ticket,
    TicketBase,
    TicketCreate,
    TicketSearch,
    TicketUpdate,
)
from otrs_gi_core.domain_models.ticket_operation import TicketOperation
from otrs_gi_core.setup.bootstrap import generate_random_password, setup_host_system
from otrs_gi_core.setup.webservices import (
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
    WebserviceBuilder,
)
from otrs_gi_core.util.errors import GenericInterfaceError

__all__ = [
    "Article",
    "BasicAuth",
    "ClientConfig",
    "ConsoleCommandRunner",
    "GenericInterfaceClient",
    "GenericInterfaceError",
    "IdName",
    "OperationUrlMap",
    "SUPPORTED_OPERATION_SPECS",
    "SUPPORTED_OPERATIONS_DOC",
    "SystemConsole",
    "Ticket",
    "TicketBase",
    "TicketCreate",
    "TicketOperation",
    "TicketSearch",
    "TicketUpdate",
    "WebserviceBuilder",
    "generate_random_password",
    "setup_host_system",
]
