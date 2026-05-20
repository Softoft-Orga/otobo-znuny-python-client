"""Deprecated compatibility package. Prefer `otobo` or `znuny`."""

from otrs_gi_core.clients.generic_interface_client import GenericInterfaceClient as OTOBOZnunyClient

__all__ = ["OTOBOZnunyClient"]
