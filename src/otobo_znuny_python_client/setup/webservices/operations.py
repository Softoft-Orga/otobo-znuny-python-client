from __future__ import annotations

from typing import Iterable

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.setup.webservices.webservice_models import OperationSpec

SUPPORTED_OPERATION_SPECS: dict[TicketOperation, OperationSpec] = {
    TicketOperation.CREATE: OperationSpec(
        operation_name="ticket-create",
        op=TicketOperation.CREATE,
        route="/tickets",
        description="Creates a new ticket.",
        methods=["POST"],
        include_ticket_data="1",
    ),
    TicketOperation.GET: OperationSpec(
        operation_name="ticket-get",
        op=TicketOperation.GET,
        route="/tickets/:TicketId",
        description="Retrieves ticket information by ID.",
        methods=["GET"],
        include_ticket_data="1",
    ),
    TicketOperation.SEARCH: OperationSpec(
        operation_name="ticket-search",
        op=TicketOperation.SEARCH,
        route="/tickets/search",
        description="Searches for tickets based on specified criteria.",
        methods=["POST"],
        include_ticket_data="1",
    ),
    TicketOperation.UPDATE: OperationSpec(
        operation_name="ticket-update",
        op=TicketOperation.UPDATE,
        route="/tickets/:TicketId",
        description="Updates an existing ticket.",
        methods=["PUT"],
        include_ticket_data="1",
    ),
}


def _build_operations_doc(specs: Iterable[OperationSpec]) -> str:
    lines = ["Supported operations and routes:"]
    for spec in specs:
        methods = ", ".join(spec.methods)
        lines.append(
            f"- {spec.operation_name}: {spec.description} "
            f"(Route: {spec.route}, Methods: {methods})"
        )
    return "\n".join(lines)


SUPPORTED_OPERATIONS_DOC = _build_operations_doc(SUPPORTED_OPERATION_SPECS.values())
