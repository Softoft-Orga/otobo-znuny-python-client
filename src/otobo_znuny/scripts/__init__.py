"""
Deprecated scripts module - use otobo_znuny.cli and otobo_znuny.setup instead.

This module provides backward compatibility imports.
"""

import warnings

# Backward compatibility imports
from ..cli.interface import ArgsBuilder, CmdResult, OtoboCommandRunner, OtoboConsole
from ..setup.bootstrap import SystemEnvironment, set_env_var
from ..setup.webservices.generator import WebServiceGenerator
from ..setup.webservices.utils import generate_enabled_operations_list

warnings.warn(
    "otobo_znuny.scripts is deprecated. Use otobo_znuny.cli and otobo_znuny.setup instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "ArgsBuilder", "CmdResult", "OtoboCommandRunner", "OtoboConsole",
    "SystemEnvironment", "set_env_var", "WebServiceGenerator", 
    "generate_enabled_operations_list"
]