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
    "ListQueues": "Admin::Queue::List",
}

PASSWORD_TO_WEAK_CODE = 2


@dataclass
class CmdResult:
    code: int = 0
    out: str = ""
    err: str = ""

    def __eq__(self, o: CmdResult) -> bool:
        return isinstance(o, CmdResult) and self.code == o.code

    @property
    def ok(self):
        return self.code == 0

    @classmethod
    def union(cls, results: list[CmdResult]) -> CmdResult:
        combined_out = "\n".join(r.out for r in results if r.out)
        combined_err = "\n".join(r.err for r in results if r.err)
        combined_code = max(r.code for r in results)
        return CmdResult(
            code=combined_code,
            out=combined_out,
            err=combined_err,
        )


class PasswordToWeak(CmdResult):
    def __init__(self) -> None:
        super().__init__(
            code=PASSWORD_TO_WEAK_CODE,
            out="",
            err="Password is too weak.",
        )


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
