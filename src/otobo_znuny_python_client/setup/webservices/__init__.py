"""Web service setup utilities."""

from __future__ import annotations

from otobo_znuny_python_client.setup.webservices.builder import (
    DEFAULT_FRAMEWORK_VERSION,
    WebserviceBuilder,
)
from otobo_znuny_python_client.setup.webservices.operations import (
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
)
from otobo_znuny_python_client.setup.webservices.utils import generate_enabled_operations_list

__all__ = [
    "DEFAULT_FRAMEWORK_VERSION",
    "SUPPORTED_OPERATION_SPECS",
    "SUPPORTED_OPERATIONS_DOC",
    "WebserviceBuilder",
    "generate_enabled_operations_list",
]
