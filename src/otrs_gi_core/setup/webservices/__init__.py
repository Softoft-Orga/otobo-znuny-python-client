"""Web service setup utilities."""

from __future__ import annotations

from otrs_gi_core.setup.webservices.builder import (
    DEFAULT_FRAMEWORK_VERSION,
    WebserviceBuilder,
)
from otrs_gi_core.setup.webservices.operations import (
    SUPPORTED_OPERATION_SPECS,
    SUPPORTED_OPERATIONS_DOC,
)
from otrs_gi_core.setup.webservices.utils import generate_enabled_operations_list

__all__ = [
    "DEFAULT_FRAMEWORK_VERSION",
    "SUPPORTED_OPERATION_SPECS",
    "SUPPORTED_OPERATIONS_DOC",
    "WebserviceBuilder",
    "generate_enabled_operations_list",
]
