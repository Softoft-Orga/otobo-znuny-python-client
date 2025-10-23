"""Web service setup utilities."""

from __future__ import annotations

from otobo_znuny_python_client.setup.webservices.generator import (
    AUTH_EXPECTATIONS_DOC,
    DEFAULT_BASIC_AUTH_PASSWORD,
    DEFAULT_BASIC_AUTH_USER,
    DEFAULT_FRAMEWORK_VERSION,
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
    WebServiceGenerator,
)
from otobo_znuny_python_client.setup.webservices.utils import generate_enabled_operations_list

__all__ = [
    "AUTH_EXPECTATIONS_DOC",
    "DEFAULT_BASIC_AUTH_PASSWORD",
    "DEFAULT_BASIC_AUTH_USER",
    "DEFAULT_FRAMEWORK_VERSION",
    "SUPPORTED_OPERATION_SPECS",
    "SUPPORTED_OPERATIONS_DOC",
    "WebServiceGenerator",
    "generate_enabled_operations_list",
]
