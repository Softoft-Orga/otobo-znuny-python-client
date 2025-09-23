from __future__ import annotations


class _Cursor:
    def execute(self, query: str) -> None:  # noqa: D401
        """Stub execute method that does nothing."""


class _Connection:
    def cursor(self) -> _Cursor:
        return _Cursor()
=======
class _DummyCursor:
    def execute(self, query: str) -> None:
        self.last_query = query


class _DummyConnection:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def cursor(self) -> _DummyCursor:
        return _DummyCursor()

    def close(self) -> None:
        pass


def connect(**kwargs) -> _Connection:  # noqa: ANN003
    return _Connection()
