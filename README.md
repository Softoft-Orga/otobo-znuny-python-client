# OTOBO and Znuny Python SDKs

This repository ships **two customer-facing Python SDKs** plus a shared GenericInterface core:

| Package | Import | Client class |
| --- | --- | --- |
| **OTOBO SDK** | `pip install otobo` then `from otobo import OTOBOClient` | `OTOBOClient` |
| **Znuny SDK** | `pip install znuny` then `from znuny import ZnunyClient` | `ZnunyClient` |
| **Compatibility (deprecated)** | `pip install otobo-znuny` then `from otobo_znuny.clients.otobo_client import OTOBOZnunyClient` | `OTOBOZnunyClient` |

Shared REST logic lives in `otrs_gi_core`. OTOBO and Znuny differ mainly in CLI console paths and setup defaults.

## Documentation

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/):

```bash
uv run --group docs mkdocs serve
```

- [OTOBO getting started](docs/getting-started-otobo.md)
- [Znuny getting started](docs/getting-started-znuny.md)
- [Migration from the combined client](docs/migration.md)

## Quick start — OTOBO

```bash
pip install otobo
```

```python
from otobo import OTOBOClient, BasicAuth, ClientConfig, TicketCreate, TicketOperation

config = ClientConfig(
    base_url="https://your-otobo-server",
    webservice_name="MyWebservice",
    operation_url_map={
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.GET: "ticket-get",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.UPDATE: "ticket-update",
    },
)

client = OTOBOClient(config)
client.login(BasicAuth(user_login="agent", password="secret"))
```

## Quick start — Znuny

```bash
pip install znuny
```

```python
from znuny import ZnunyClient, BasicAuth, ClientConfig, TicketOperation

client = ZnunyClient(
    ClientConfig(
        base_url="https://your-znuny-server",
        webservice_name="MyWebservice",
        operation_url_map={
            TicketOperation.CREATE: "ticket-create",
            TicketOperation.GET: "ticket-get",
            TicketOperation.SEARCH: "ticket-search",
            TicketOperation.UPDATE: "ticket-update",
        },
    )
)
```

## CLI tools

```bash
otobo-cli setup-system
znuny-cli setup-system
```

The legacy combined CLI remains available via `python -m otobo_znuny.cli.app`.

## Features

- Async HTTP via `httpx.AsyncClient`
- Pydantic v2 models for requests and responses
- Ticket CRUD: create, search, get, update
- `search_and_get` helper
- Webservice YAML builder and interactive setup wizard

## License

MIT © Softoft, Tobias A. Bueck
