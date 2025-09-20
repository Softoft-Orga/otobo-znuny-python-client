from enum import Enum, IntEnum
from typing import Self


class OtoboEntity(IntEnum):
    label: str

    def __new__(cls, id_: int, label: str) -> Self:
        obj = object.__new__(cls)
        obj._value_ = id_
        obj.label = label
        return obj

    @property
    def id(self) -> int:
        return self._value_

    def __str__(self) -> str:
        return self.label
