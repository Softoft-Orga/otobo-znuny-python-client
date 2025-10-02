from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import ModuleType

import pytest


if "mariadb" not in sys.modules:
    mariadb_stub = ModuleType("mariadb")

    class _Cursor:
        def execute(self, *_args, **_kwargs) -> None:
            return None

    class _Connection:
        def cursor(self) -> _Cursor:
            return _Cursor()

        def close(self) -> None:
            return None

    def _connect(*_args, **_kwargs) -> _Connection:
        return _Connection()

    mariadb_stub.connect = _connect  # type: ignore[attr-defined]
    mariadb_stub.OperationalError = Exception  # type: ignore[attr-defined]
    sys.modules["mariadb"] = mariadb_stub


# Removed conftest stub - actual conftest.py is now properly configured

import typing

try:
    from typing_extensions import Generator as _CompatGenerator
except Exception:  # pragma: no cover
    _CompatGenerator = None  # type: ignore[assignment]

if _CompatGenerator is not None:
    typing.Generator = _CompatGenerator  # type: ignore[assignment]
