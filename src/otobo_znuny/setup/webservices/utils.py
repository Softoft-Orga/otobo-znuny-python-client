from otobo_znuny.domain_models.ticket_operation import TicketOperation

OPERATIONS: dict[str, TicketOperation] = {
    "get": TicketOperation.GET,
    "search": TicketOperation.SEARCH,
    "create": TicketOperation.CREATE,
    "update": TicketOperation.UPDATE,
}

def generate_enabled_operations_list(
        enabled_operations: list[str],
) -> list[TicketOperation]:
    return [OPERATIONS[s.lower().strip()] for s in enabled_operations if s.lower().strip() in OPERATIONS]
