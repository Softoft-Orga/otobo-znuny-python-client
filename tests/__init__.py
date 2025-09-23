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


if "tests.conftest" not in sys.modules:
    conftest_stub = ModuleType("tests.conftest")

    def _event_loop():
        loop = asyncio.new_event_loop()
        try:
            yield loop
        finally:
            loop.close()

    conftest_stub.event_loop = pytest.fixture(scope="session")(_event_loop)
    conftest_stub.__file__ = str(Path(__file__).with_name("conftest.py"))
    sys.modules["tests.conftest"] = conftest_stub

import typing

try:
    from typing_extensions import Generator as _CompatGenerator
except Exception:  # pragma: no cover
    _CompatGenerator = None  # type: ignore[assignment]

if _CompatGenerator is not None:
    typing.Generator = _CompatGenerator  # type: ignore[assignment]
