# OTOBO / Znuny Python SDKs - Agent Guide

This file takes precedence over the repository-root `AGENTS.md` for work inside
`otobo-znuny-python-client/`.

## Purpose

Python SDKs for OTOBO and Znuny GenericInterface REST APIs. Shared logic is in
`otrs_gi_core`; product-facing imports are `otobo` and `znuny`. Legacy paths
`otobo_znuny` and `otobo_znuny_python_client` remain as compatibility shims.

## Layout

- `src/otrs_gi_core/` — shared async client, models, mappers, CLI core, setup
- `src/otobo/` — OTOBO-branded public API and CLI (`otobo-cli`)
- `src/znuny/` — Znuny-branded public API and CLI (`znuny-cli`)
- `src/otobo_znuny/` — deprecated compatibility re-exports
- `src/otobo_znuny_python_client/` — deprecated compatibility re-exports
- `tests/unit/` — isolated tests; `tests/e2e/` needs a live system
- `docs/` — MkDocs source; start at `docs/index.md`

## Commands

```powershell
uv sync --group dev
uv run pytest tests/unit
uv run ruff check .
uv run mypy src/otrs_gi_core src/otobo src/znuny
```

## Guardrails

- Keep shared REST behavior in `otrs_gi_core`; product differences belong in
  `otobo` / `znuny` CLI environment defaults only unless behavior truly diverges.
- Preserve legacy import paths unless explicitly removing a compatibility window.
- Do not commit credentials, `.env`, or generated local configs.
