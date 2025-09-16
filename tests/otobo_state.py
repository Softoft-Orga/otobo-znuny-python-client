from enum import Enum
from typing import Self

from tests.otobo_entity import OtoboEntity


class State(OtoboEntity):
    NEW = 1, "new"
    CLOSED_SUCCESSFUL = 2, "closed successful"
    CLOSED_UNSUCCESSFUL = 3, "closed unsuccessful"
    OPEN = 4, "open"
    REMOVED = 5, "removed"
    PENDING_REMINDER = 6, "pending reminder"
    PENDING_AUTO_CLOSE_PLUS = 7, "pending auto close+"
    PENDING_AUTO_CLOSE_MINUS = 8, "pending auto close-"
    MERGED = 9, "merged"
