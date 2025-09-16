from enum import Enum
from typing import Any


class TicketOperation(Enum):
    CREATE = ("TicketCreate", "Ticket::TicketCreate")
    SEARCH = ("TicketSearch", "Ticket::TicketSearch")
    GET = ("TicketGet", "Ticket::TicketGet")
    UPDATE = ("TicketUpdate", "Ticket::TicketUpdate")

    def __new__(cls, name: str, operation_type: str):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.operation_type = operation_type
        return obj

    @property
    def type(self) -> str:
        return self.operation_type

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TicketOperation):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False
