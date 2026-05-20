"""Python SDK for Znuny GenericInterface REST APIs."""

from otrs_gi_core.clients.generic_interface_client import GenericInterfaceClient as ZnunyClient
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
from otrs_gi_core.setup.bootstrap import generate_random_password, setup_host_system as setup_znuny_system
from otrs_gi_core.setup.webservices import (
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
    WebserviceBuilder,
)
from otrs_gi_core.util.errors import GenericInterfaceError as ZnunyError

__all__ = [
    "Article",
    "BasicAuth",
    "ClientConfig",
    "IdName",
    "OperationUrlMap",
    "SUPPORTED_OPERATION_SPECS",
    "SUPPORTED_OPERATIONS_DOC",
    "Ticket",
    "TicketBase",
    "TicketCreate",
    "TicketOperation",
    "TicketSearch",
    "TicketUpdate",
    "WebserviceBuilder",
    "ZnunyClient",
    "ZnunyError",
    "generate_random_password",
    "setup_znuny_system",
]
