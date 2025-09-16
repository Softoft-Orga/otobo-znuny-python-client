from tests.e2e.demo_system.otobo_entity import OtoboEntity


class TicketType(OtoboEntity):
    UNCLASSIFIED = 1, "Unclassified"
    INCIDENT = 2, "Incident"
