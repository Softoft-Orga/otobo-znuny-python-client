"""
Deprecated scripts module - use otobo_znuny_python_client.cli and otobo_znuny_python_client.setup instead.

This module provides backward compatibility imports.
"""

import warnings

# Backward compatibility imports
from otobo_znuny_python_client.cli.interface import ArgsBuilder, CmdResult, OtoboCommandRunner, OtoboConsole
from otobo_znuny_python_client.setup.bootstrap import SystemEnvironment, set_env_var
from otobo_znuny_python_client.setup.webservices.builder import WebserviceBuilder
from otobo_znuny_python_client.setup.webservices.utils import generate_enabled_operations_list

warnings.warn(
    "otobo_znuny_python_client.scripts is deprecated. Use otobo_znuny_python_client.cli and otobo_znuny_python_client.setup instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ArgsBuilder",
    "CmdResult",
    "OtoboCommandRunner",
    "OtoboConsole",
    "SystemEnvironment",
    "WebserviceBuilder",
    "generate_enabled_operations_list",
    "set_env_var",
]
