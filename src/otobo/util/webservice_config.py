from pathlib import Path
from typing import Dict, Any
import yaml

"""Utilities for reading OTOBO Webservice configuration files.

The original implementation imported from the top-level :mod:`otobo`
package.  This caused a circular import when :mod:`otobo.__init__` tried to
expose :func:`create_otobo_client_config` while this module simultaneously
imported from :mod:`otobo`.  Using relative imports resolves the cycle and
keeps the module usable when the package is imported directly from the
source tree.
"""

from ..models.client_config_models import TicketOperation, OTOBOClientConfig
from ..models.request_models import AuthData

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
