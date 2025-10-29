from __future__ import annotations

from typing import Iterable

from domain_models.ticket_operation import TicketOperation
from setup.webservices.webservice_models import OperationSpec

SUPPORTED_OPERATION_SPECS: dict[TicketOperation, OperationSpec] = {
    TicketOperation.GET: OperationSpec(
        op=TicketOperation.GET,
        route="/tickets/:TicketID",
        description="Get ticket details by ID.",
        methods=["GET"],
        include_ticket_data="1",
    ),
    TicketOperation.SEARCH: OperationSpec(
        op=TicketOperation.SEARCH,
        route="/tickets/search",
        description="Search for tickets using the request payload as criteria.",
        methods=["POST"],
        include_ticket_data="1",
    ),
    TicketOperation.CREATE: OperationSpec(
        op=TicketOperation.CREATE,
        route="/tickets",
        description="Create a new ticket from the supplied Ticket and Article data.",
        methods=["POST"],
        include_ticket_data="1",
    ),
    TicketOperation.UPDATE: OperationSpec(
        op=TicketOperation.UPDATE,
        route="/tickets/:TicketID",
        description="Update an existing ticket identified by the path parameter.",
        methods=["PUT", "PATCH"],
        include_ticket_data="1",
    ),
}


def _build_operations_doc(specs: Iterable[OperationSpec]) -> str:
    lines = ["Supported operations and routes:"]
    for spec in specs:
        methods = ", ".join(spec.methods)
        lines.append(
            f"- {spec.op.name.lower()}: {spec.description}"
            f" (Route: {spec.route}, Methods: {methods})"
        )
    return "\n".join(lines)


SUPPORTED_OPERATIONS_DOC = _build_operations_doc(SUPPORTED_OPERATION_SPECS.values())
