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


def connect(*args, **kwargs) -> _DummyConnection:
    return _DummyConnection(*args, **kwargs)
