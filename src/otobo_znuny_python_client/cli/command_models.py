from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Permission = Literal["ro", "move_into", "create", "owner", "priority", "rw"]

OTOBO_COMMANDS = {
    "AddUser": "Admin::User::Add",
    "AddGroup": "Admin::Group::Add",
    "AddQueue": "Admin::Queue::Add",
    "AddWebservice": "Admin::WebService::Add",
    "LinkUserToGroup": "Admin::Group::UserLink",
}


@dataclass
class CmdResult:
    ok: bool
    code: int
    out: str
    err: str


class ArgsBuilder:
    def __init__(self):
        self._parts: list[str] = []

    def opt(self, name: str, value: str | int | Path | None = None) -> ArgsBuilder:
        if value is None:
            self._parts.append(name)
        else:
            self._parts.extend([name, str(value)])
        return self

    def opt_if(self, name: str, value: str | int | Path | None) -> ArgsBuilder:
        if value is not None:
            self._parts.extend([name, str(value)])
        return self

    def repeat_if(self, name: str, values: list[str | int | Path] | None) -> ArgsBuilder:
        if values:
            for v in values:
                self._parts.extend([name, str(v)])
        return self

    def flag(self, name: str, enabled: bool = True) -> ArgsBuilder:
        if enabled:
            self._parts.append(name)
        return self

    def repeat(self, name: str, values: list[str | int | Path]) -> ArgsBuilder:
        for v in values:
            self._parts.extend([name, str(v)])
        return self

    def to_list(self) -> list[str]:
        return list(self._parts)
