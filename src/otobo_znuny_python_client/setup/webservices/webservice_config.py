from pathlib import Path
from typing import Any

import yaml

from otobo_znuny_python_client.domain_models.otobo_client_config import ClientConfig
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation

TYPE_TO_ENUM = {op.type: op for op in TicketOperation}


def _read_yaml(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _extract_operations_by_type(ws: dict[str, Any]) -> dict[TicketOperation, str]:
    ops = ws.get("Provider", {}).get("Operation", {}) or {}
    result: dict[TicketOperation, str] = {}
    for endpoint_name, cfg in ops.items():
        type_str = str((cfg or {}).get("Type", "")).strip()
        enum_key = TYPE_TO_ENUM.get(type_str)
        if enum_key:
            result[enum_key] = str(endpoint_name)
    return result


def create_otobo_client_config(
        webservice_yaml_path: str | Path,
        base_url: str,
        service: str,
) -> ClientConfig:
    data = _read_yaml(webservice_yaml_path)
    operations = _extract_operations_by_type(data)
    if not operations:
        raise ValueError("No supported ticket operations found in webservice YAML.")
    return ClientConfig(
        base_url=base_url,
        webservice_name=service,
        operation_url_map=operations,
    )
