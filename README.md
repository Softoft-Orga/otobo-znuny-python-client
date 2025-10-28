# Python OTOBO Client Library

An asynchronous Python client for interacting with the OTOBO / Znuny REST API. Built with `httpx` and `pydantic` for
type safety
and ease of use.

## Documentation

The project documentation is built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. You can browse the
Markdown sources locally or serve the documentation site with:

```bash
uv run --group docs mkdocs serve
```

The published sections include:

- [Getting started (English)](docs/getting-started.en.md)
- [Library overview](docs/library-overview.md)

## Features

* **Asynchronous** HTTP requests using `httpx.AsyncClient`
* **Pydantic** models for request and response data validation
* Full CRUD operations for tickets:

    * `TicketCreate`
    * `TicketSearch`
    * `TicketGet`
    * `TicketUpdate`
* **Error handling** via `OTOBOError` for API errors
* Utility method `search_and_get` to combine search results with detailed retrieval

## Installation

Install from PyPI:

```bash
pip install otobo_znuny_python_client
```

## License

MIT © Softoft, Tobias A. Bueck
