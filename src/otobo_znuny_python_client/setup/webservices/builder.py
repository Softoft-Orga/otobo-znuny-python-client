from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import yaml

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.operations import SUPPORTED_OPERATION_SPECS
from otobo_znuny_python_client.setup.webservices.webservice_models import OperationSpec

DEFAULT_FRAMEWORK_VERSION = "11.0.11"

_INBOUND_MAPPING_BASE: dict[str, Any] = {
    "Type": "Simple",
    "Config": {
        "KeyMapDefault": {"MapTo": "", "MapType": "Keep"},
        "KeyMapExact": {"UserLogin": "UserLogin"},
        "ValueMapDefault": {"MapTo": "", "MapType": "Keep"},
    },
}

_OUTBOUND_MAPPING: dict[str, Any] = {
    "Type": "Simple",
    "Config": {
        "KeyMapDefault": {"MapTo": "", "MapType": "Keep"},
        "ValueMapDefault": {"MapTo": "", "MapType": "Keep"},
    },
}

_TRANSPORT_CONFIG_TEMPLATE: dict[str, Any] = {
    "AdditionalHeaders": None,
    "KeepAlive": "",
    "MaxLength": "1000000",
    "OutboundHeaders": {},
    "RouteOperationMapping": {},
}


class WebserviceBuilder:
    """Builder for OTOBO/Znuny ticket webservice configurations."""

    def __init__(
            self,
            name: str = "OpenTicketAI",
            *,
            framework_version: str = DEFAULT_FRAMEWORK_VERSION,
            operation_specs: Mapping[TicketOperation, OperationSpec] | None = None,
    ) -> None:
        self._name = name
        self._framework_version = framework_version
        self._operation_specs = dict(operation_specs or SUPPORTED_OPERATION_SPECS)
        self._enabled_operations: list[TicketOperation] = []
        self._restricted_user: str | None = None

    def set_name(self, name: str) -> WebserviceBuilder:
        self._name = name
        return self

    def set_framework_version(self, framework_version: str) -> WebserviceBuilder:
        self._framework_version = framework_version
        return self

    def set_restricted_by(self, username: str | None) -> WebserviceBuilder:
        self._restricted_user = username or None
        return self

    def clear_restriction(self) -> WebserviceBuilder:
        self._restricted_user = None
        return self

    def enable_operation(self, operation: TicketOperation) -> WebserviceBuilder:
        if operation not in self._operation_specs:
            raise ValueError(f"Unsupported operation: {operation}")
        if operation not in self._enabled_operations:
            self._enabled_operations.append(operation)
        return self

    def enable_operations(self, *operations: TicketOperation) -> WebserviceBuilder:
        for operation in operations:
            self.enable_operation(operation)
        return self

    def reset_operations(self) -> WebserviceBuilder:
        self._enabled_operations.clear()
        return self

    def build(self) -> dict[str, Any]:
        if not self._enabled_operations:
            raise ValueError("No operations have been enabled for the webservice")

        transport_config = deepcopy(_TRANSPORT_CONFIG_TEMPLATE)
        transport_config["RouteOperationMapping"] = {}

        config: dict[str, Any] = {
            "Debugger": {
                "DebugThreshold": "debug",
                "TestMode": "0",
            },
            "Description": self._build_description(),
            "FrameworkVersion": self._framework_version,
            "Provider": {
                "Operation": {},
                "Transport": {
                    "Config": transport_config,
                    "Type": "HTTP::REST",
                },
            },
            "RemoteSystem": "",
            "Requester": {
                "Transport": {"Type": ""},
            },
        }

        route_mapping: dict[str, Any] = config["Provider"]["Transport"]["Config"]["RouteOperationMapping"]
        operations_map: dict[str, Any] = config["Provider"]["Operation"]

        for operation in self._enabled_operations:
            spec = self._operation_specs[operation]
            operations_map[spec.operation_name] = self._build_operation_config(spec)
            route_mapping[spec.operation_name] = {
                "Route": spec.route,
                "RequestMethod": spec.methods,
            }

        return config

    def dump_yaml(self, config: dict[str, Any]) -> str:
        return yaml.dump(
            config,
            allow_unicode=True,
            sort_keys=False,
            Dumper=_NoAliasDumper,
            indent=2,
        )

    def save_to_file(self, config: dict[str, Any], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.dump_yaml(config), encoding="utf-8")

    def _build_description(self) -> str:
        base = f"Webservice for '{self._name}'."
        if self._restricted_user:
            return f"{base} Restricted to user '{self._restricted_user}'."
        return base

    def _build_operation_config(self, spec: OperationSpec) -> dict[str, Any]:
        return {
            "Type": spec.op.type,
            "Description": spec.description,
            "IncludeTicketData": spec.include_ticket_data,
            "MappingInbound": self._build_inbound_mapping(),
            "MappingOutbound": deepcopy(_OUTBOUND_MAPPING),
        }

    def _build_inbound_mapping(self) -> dict[str, Any]:
        mapping = deepcopy(_INBOUND_MAPPING_BASE)
        if self._restricted_user:
            mapping["Config"]["ValueMap"] = {
                "UserLogin": {
                    "ValueMapRegEx": {".*": self._restricted_user},
                }
            }
        return mapping


class _NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:  # pragma: no cover - inherited API
        return True
