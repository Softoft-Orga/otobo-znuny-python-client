from pathlib import Path
from typing import Dict, Any
import yaml

from otobo.models.client_config_models import TicketOperation, OTOBOClientConfig
from otobo.models.request_models import AuthData

TYPE_TO_ENUM = {op.type: op for op in TicketOperation}


def _read_yaml(path: str | Path) -> Dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _extract_operations_by_type(ws: Dict[str, Any]) -> Dict[TicketOperation, str]:
    ops = ws.get("Provider", {}).get("Operation", {}) or {}
    result: Dict[TicketOperation, str] = {}
    for endpoint_name, cfg in ops.items():
        type_str = str((cfg or {}).get("Type", "")).strip()
        enum_key = TYPE_TO_ENUM.get(type_str)
        if enum_key:
            result[enum_key] = str(endpoint_name)
    return result


def create_otobo_client_config(
        webservice_yaml_path: str | Path,
        base_url: str,
        auth: AuthData,
        service: str,
) -> OTOBOClientConfig:
    data = _read_yaml(webservice_yaml_path)
    operations = _extract_operations_by_type(data)
    if not operations:
        raise ValueError("No supported ticket operations found in webservice YAML.")
    return OTOBOClientConfig(
        base_url=base_url,
        service=service,
        auth=auth,
        operations=operations,
    )
