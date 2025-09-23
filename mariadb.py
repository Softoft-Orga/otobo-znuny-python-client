from __future__ import annotations


class _Cursor:
    def execute(self, query: str) -> None:  # noqa: D401
        """Stub execute method that does nothing."""


class _Connection:
    def cursor(self) -> _Cursor:
        return _Cursor()

    def close(self) -> None:
        pass


def connect(**kwargs) -> _Connection:  # noqa: ANN003
    return _Connection()

