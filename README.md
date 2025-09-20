# Python OTOBO Client Library

An asynchronous Python client for interacting with the OTOBO / Znuny REST API. Built with `httpx` and `pydantic` for type safety
and ease of use.

## Documentation

- [Getting started (English)](docs/getting-started.en.md)
- [Einstieg (Deutsch)](docs/getting-started.de.md)

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
pip install otobo_znuny
```

## License

MIT © Softoft, Tobias A. Bueck
