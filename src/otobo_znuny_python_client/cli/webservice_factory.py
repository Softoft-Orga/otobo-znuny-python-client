from __future__ import annotations

from typing import Iterable

from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation


def create_webservice(
        webservice_name: str,
        enabled_operations: Iterable[TicketOperation],
        restriction_by_user: str | None,
) -> None:
    """Create or configure a webservice for the CLI.

    This function acts as a placeholder that can be extended with the
    actual implementation responsible for creating a webservice within
    the target OTOBO/Znuny system.
    """

    # Implementation will be provided in a future iteration.
    # For now, this function intentionally does nothing.
    return None
