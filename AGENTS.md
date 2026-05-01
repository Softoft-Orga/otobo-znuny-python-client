# OTOBO Znuny Python Client - Agent Guide

This file takes precedence over the repository-root `AGENTS.md` for work inside
`otobo-znuny-python-client/`.

## Purpose

This project is the Python client library for the OTOBO / Znuny REST API. It is
a reusable package, not the OTAI Runtime or Studio. Keep changes focused on the
client library, CLI helpers, documentation, and tests for OTOBO/Znuny API usage.

## Stack

- Python 3.11+
- `httpx` for async HTTP calls
- Pydantic v2 for request, response, and domain models
- Typer-based CLI helpers
- pytest / pytest-asyncio for tests
- MkDocs Material for documentation

## Layout

- `src/otobo_znuny/` is the primary package.
- `src/otobo_znuny_python_client/` contains compatibility package paths; do not
remove or rename them without checking downstream import compatibility.
- `tests/unit/` contains isolated tests.
- `tests/e2e/` contains tests that may require a real or local OTOBO/Znuny
system.
- `docs/` contains MkDocs source content; start at `[docs/index.md](./docs/index.md)`.

## Commands

```powershell
uv sync --group dev
uv run pytest
uv run ruff check .
uv run mypy .
uv run --group docs mkdocs serve
```

Run unit tests for focused library changes. Run E2E tests only when the required
OTOBO/Znuny test system and credentials are available.

## Guardrails

- Preserve the public API unless the task explicitly asks for a breaking change.
- Keep async client behavior async; do not add blocking network calls to client
paths.
- Model API payloads with Pydantic instead of untyped dictionaries when the shape
is stable.
- Do not commit real OTOBO/Znuny credentials, generated local configs, session
data, or `.env` files.
- Update `docs/` and README examples when CLI behavior, configuration, or public
client APIs change.

