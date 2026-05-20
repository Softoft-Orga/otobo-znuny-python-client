"""One-off migration: copy otobo_znuny shared modules into otrs_gi_core."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SOURCE_PKG = SRC / "otobo_znuny"
TARGET_PKG = SRC / "otrs_gi_core"

# Shared modules to copy (relative paths under otobo_znuny/)
SHARED_PATHS = [
    "domain_models/basic_auth_model.py",
    "domain_models/otobo_client_config.py",
    "domain_models/ticket_models.py",
    "domain_models/ticket_operation.py",
    "models/base_models.py",
    "models/request_models.py",
    "models/response_models.py",
    "models/ticket_models.py",
    "util/safe_base_model.py",
    "mappers.py",
    "clients/otobo_client.py",
    "setup/config.py",
    "setup/bootstrap.py",
    "setup/__init__.py",
    "setup/webservices/__init__.py",
    "setup/webservices/builder.py",
    "setup/webservices/operations.py",
    "setup/webservices/utils.py",
    "setup/webservices/webservice_config.py",
    "setup/webservices/webservice_models.py",
    "cli/command_models.py",
    "cli/otobo_command_runner.py",
    "cli/otobo_console.py",
]

IMPORT_REPLACEMENTS = [
    (r"\botobo_znuny\b", "otrs_gi_core"),
    (r"\bfrom models\b", "from otrs_gi_core.models"),
    (r"\bfrom domain_models\b", "from otrs_gi_core.domain_models"),
    (r"\botobo_znuny_python_client\b", "otrs_gi_core"),
]

CONTENT_REPLACEMENTS = [
    ("class OTOBOError", "class GenericInterfaceError"),
    ("OTOBOError", "GenericInterfaceError"),
    ("class OTOBOZnunyClient", "class GenericInterfaceClient"),
    ("OTOBOZnunyClient", "GenericInterfaceClient"),
    ("class OtoboCommandRunner", "class ConsoleCommandRunner"),
    ("OtoboCommandRunner", "ConsoleCommandRunner"),
    ("class OtoboConsole", "class SystemConsole"),
    ("OtoboConsole", "SystemConsole"),
    ("class OtoboSystem", "class HostSystem"),
    ("OtoboSystem", "HostSystem"),
    ("setup_otobo_system", "setup_host_system"),
    ("OTOBO_COMMANDS", "CONSOLE_COMMANDS"),
    ("otobo_client_config.py", "client_config.py"),
    ("otobo_errors.py", "errors.py"),
    ("otobo_command_runner.py", "command_runner.py"),
    ("otobo_console.py", "system_console.py"),
]


def transform(content: str, rel_path: str) -> str:
    for pattern, repl in IMPORT_REPLACEMENTS:
        content = re.sub(pattern, repl, content)
    for old, new in CONTENT_REPLACEMENTS:
        content = content.replace(old, new)
    if rel_path.endswith("otobo_client_config.py"):
        content = content.replace("client_config.py", "client_config.py")
    if rel_path.endswith("clients/otobo_client.py"):
        content = content.replace(
            "clients/otobo_client.py",
            "clients/generic_interface_client.py",
        )
    return content


def main() -> None:
    if TARGET_PKG.exists():
        shutil.rmtree(TARGET_PKG)
    TARGET_PKG.mkdir(parents=True)

    # util/errors.py (from otobo_errors)
    errors_src = SOURCE_PKG / "util" / "otobo_errors.py"
    errors_dst = TARGET_PKG / "util" / "errors.py"
    errors_dst.parent.mkdir(parents=True, exist_ok=True)
    content = errors_src.read_text(encoding="utf-8")
    content = content.replace("class OTOBOError", "class GenericInterfaceError")
    errors_dst.write_text(content, encoding="utf-8")

    # domain_models/client_config.py (from otobo_client_config)
    cfg_src = SOURCE_PKG / "domain_models" / "otobo_client_config.py"
    cfg_dst = TARGET_PKG / "domain_models" / "client_config.py"
    cfg_dst.parent.mkdir(parents=True, exist_ok=True)
    content = transform(cfg_src.read_text(encoding="utf-8"), "domain_models/otobo_client_config.py")
    cfg_dst.write_text(content, encoding="utf-8")

    # clients/generic_interface_client.py
    client_src = SOURCE_PKG / "clients" / "otobo_client.py"
    client_dst = TARGET_PKG / "clients" / "generic_interface_client.py"
    client_dst.parent.mkdir(parents=True, exist_ok=True)
    content = transform(client_src.read_text(encoding="utf-8"), "clients/otobo_client.py")
    content = content.replace(
        "from otrs_gi_core.util.otobo_errors import GenericInterfaceError",
        "from otrs_gi_core.util.errors import GenericInterfaceError",
    )
    client_dst.write_text(content, encoding="utf-8")

    skip = {
        "domain_models/otobo_client_config.py",
        "clients/otobo_client.py",
        "util/otobo_errors.py",
    }

    for rel in SHARED_PATHS:
        if rel in skip:
            continue
        src = SOURCE_PKG / rel
        dst_rel = rel
        if rel == "cli/otobo_command_runner.py":
            dst_rel = "cli/command_runner.py"
        elif rel == "cli/otobo_console.py":
            dst_rel = "cli/system_console.py"
        dst = TARGET_PKG / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = transform(src.read_text(encoding="utf-8"), rel)
        dst.write_text(content, encoding="utf-8")

    # Package __init__ files
    (TARGET_PKG / "__init__.py").write_text(
        '"""Shared OTRS GenericInterface core for OTOBO and Znuny Python SDKs."""\n',
        encoding="utf-8",
    )
    for sub in ["clients", "domain_models", "models", "util", "setup", "setup/webservices", "cli"]:
        init = TARGET_PKG / sub / "__init__.py"
        init.parent.mkdir(parents=True, exist_ok=True)
        if not init.exists():
            init.write_text("", encoding="utf-8")

    print(f"Created {TARGET_PKG}")


if __name__ == "__main__":
    main()
