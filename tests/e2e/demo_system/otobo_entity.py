from enum import Enum


class OtoboEntity(Enum):
    def __new__(cls, id_: int, label: str):
        obj = object.__new__(cls)
        obj._value_ = id_
        obj.label = label
        return obj

    @property
    def id(self) -> int:
        return self.value

    def __str__(self) -> str:
        return self.label
