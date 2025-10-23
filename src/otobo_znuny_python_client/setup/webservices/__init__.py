"""Web service setup utilities."""

from __future__ import annotations

from otobo_znuny_python_client.setup.webservices.generator import WebServiceGenerator
from otobo_znuny_python_client.setup.webservices.utils import generate_enabled_operations_list

__all__ = ["WebServiceGenerator", "generate_enabled_operations_list"]
