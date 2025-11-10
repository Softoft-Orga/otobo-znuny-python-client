# OTOBO/Znuny Python Client Library Documentation

This document describes the architecture and usage patterns of the asynchronous Python client for the OTOBO/Znuny REST API that ships with this repository. It supplements the quick-start guides and focuses on the public programming interface exposed by the package.

## Core Concepts

The client wraps the OTOBO and Znuny "GenericInterface" web service endpoints. It is built on top of [`httpx.AsyncClient`](https://www.python-httpx.org/) and relies on Pydantic models for type-safe payloads and responses. The key building blocks are:

- **`OTOBOZnunyClient`** – orchestrates HTTP requests and exposes high-level ticket operations such as create, get, update, and search. 【F:src/otobo/clients/otobo_client.py†L27-L114】
- **Domain models** – validate and normalize the data you send to or receive from the API. They cover ticket entities (`TicketCreate`, `TicketUpdate`, `TicketSearch`, `Ticket`), articles, and supporting types like `IdName` and `DynamicFieldFilter`. 【F:src/otobo/domain_models/ticket_models.py†L1-L87】
- **Configuration and authentication** – the `ClientConfig` records the base URL, web service name, and ticket operation endpoints, while `BasicAuth` stores the user credentials. 【F:src/otobo/domain_models/otobo_client_config.py†L8-L14】【F:src/otobo/domain_models/basic_auth_model.py†L1-L8】
- **Error handling** – API-level errors are mapped to the custom `OTOBOError` exception, allowing you to distinguish service errors from transport failures. 【F:src/otobo/util/otobo_errors.py†L1-L7】【F:src/otobo/clients/otobo_client.py†L45-L73】

## Installation

Install the package from PyPI:

```bash
pip install otobo_znuny
```

After installation, import the client from `otobo.clients.otobo_client` or rely on the package's entry points.

## Configuring the Client

Create a `ClientConfig` instance to describe how the client should talk to your web service. The `operation_url_map` maps a `TicketOperation` enum member to the relative path of the GenericInterface operation.

```python
from otobo.clients.otobo_client import OTOBOZnunyClient
from otobo.domain_models.otobo_client_config import ClientConfig
from otobo.domain_models.ticket_operation import TicketOperation

config = ClientConfig(
    base_url="https://helpdesk.example/api",
    webservice_name="GenericTicket",
    operation_url_map={
        TicketOperation.CREATE: "TicketCreate",
        TicketOperation.SEARCH: "TicketSearch",
        TicketOperation.GET: "TicketGet",
        TicketOperation.UPDATE: "TicketUpdate",
    },
)
client = OTOBOZnunyClient(config)
```

The mapping keys are stable enums whose values mirror the GenericInterface operation names. 【F:src/otobo/domain_models/ticket_operation.py†L1-L28】 The client trims trailing slashes from the base URL and generates request URLs like `https://helpdesk.example/api/Webservice/GenericTicket/TicketCreate`. 【F:src/otobo/clients/otobo_client.py†L30-L41】

## Authenticating

Before invoking any API call, provide credentials via `login`. The password is stored as a `SecretStr`, shielding it from accidental log output.

```python
from otobo.domain_models.basic_auth_model import BasicAuth

auth = BasicAuth(user_login="api-user", password="super-secret")
client.login(auth)
```

The client automatically injects the serialized credentials into every request payload and raises a `RuntimeError` if you attempt an operation without logging in first. 【F:src/otobo/clients/otobo_client.py†L43-L73】 To drop the credentials (for instance, before reusing the client for another user), call `logout()`.

## Using the Client as an Async Context Manager

`OTOBOZnunyClient` holds an `httpx.AsyncClient`. Either pass your own instance (for custom timeouts or transport adapters) or let the library construct one. The client implements `__aenter__`/`__aexit__`, so you can use it in an async context manager to ensure the underlying HTTP client is closed properly.

```python
import asyncio

async def main():
    client.login(auth)
    async with client:
        ...  # perform operations

asyncio.run(main())
```

You can also close the client manually by calling `await client.aclose()`. 【F:src/otobo/clients/otobo_client.py†L106-L114】

## Working with Tickets

Ticket models share a `TicketBase` superclass that defines common fields such as queue, state, priority, owner, and dynamic fields. 【F:src/otobo/domain_models/ticket_models.py†L26-L63】 Each concrete model specializes the payload for a specific workflow:

- `TicketCreate` – used to create new tickets, optionally containing a first article. 【F:src/otobo/domain_models/ticket_models.py†L47-L54】
- `TicketUpdate` – updates existing tickets by ID or number. 【F:src/otobo/domain_models/ticket_models.py†L57-L64】
- `Ticket` – represents a full ticket as returned by the API, including the server-assigned ID and a list of articles. 【F:src/otobo/domain_models/ticket_models.py†L66-L72】

### Creating a Ticket

```python
from otobo.domain_models.ticket_models import Article, IdName, TicketCreate

create_payload = TicketCreate(
    title="Sample request",
    queue=IdName(name="Raw"),
    customer_user="customer@example.com",
    article=Article(
        from_addr="customer@example.com",
        subject="Example",
        body="Hello, world!",
        content_type="text/plain; charset=utf-8",
    ),
)

ticket = await client.create_ticket(create_payload)
```

The client converts the domain model to the GenericInterface schema and returns a parsed `Ticket`. If the service does not return a ticket in the response, a `RuntimeError` is raised to highlight the unexpected state. 【F:src/otobo/clients/otobo_client.py†L75-L96】

### Retrieving and Updating Tickets

```python
ticket = await client.get_ticket(12345)

update_payload = TicketUpdate(
    id=ticket.id,
    state=IdName(name="closed successful"),
)
updated_ticket = await client.update_ticket(update_payload)
```

`get_ticket` enforces that exactly one ticket is returned for the given identifier, while `update_ticket` mirrors the create flow and raises if the API omits the updated ticket. 【F:src/otobo/clients/otobo_client.py†L96-L105】

## Searching Tickets

`TicketSearch` combines common filters (numbers, queues, states, priorities, etc.) with a configurable limit. You can also supply dynamic field filters using `DynamicFieldFilter`, which supports equality, pattern, and range comparisons.

```python
from otobo.domain_models.ticket_models import DynamicFieldFilter, TicketSearch, IdName

search = TicketSearch(
    queues=[IdName(name="Raw")],
    priorities=[IdName(name="3 normal")],
    dynamic_fields=[
        DynamicFieldFilter(field_name="OrderID", equals="ABC-42"),
    ],
)

matching_ids = await client.search_tickets(search)
full_tickets = await client.search_and_get(search)
```

The `search_tickets` call returns a list of numeric ticket IDs, defaulting to an empty list when the response omits the `TicketID` field. The convenience helper `search_and_get` chains a search and individual `get_ticket` calls using `asyncio.gather` to fetch the complete ticket payloads concurrently. 【F:src/otobo/clients/otobo_client.py†L100-L105】【F:src/otobo/domain_models/ticket_models.py†L74-L87】

## Handling Dynamic Fields

Dynamic fields are expressed as simple `dict[str, str]` in the domain models. The mapper functions convert them to the GenericInterface format (`WsDynamicField`) automatically, so you only need to provide the desired key/value pairs or filters in the high-level models. 【F:src/otobo/mappers.py†L26-L89】【F:src/otobo/domain_models/ticket_models.py†L34-L63】

## Error Handling and Retries

`OTOBOZnunyClient` inspects every response for an `Error` object before validating it against the expected Pydantic model. When an error is found, it raises `OTOBOError` with the OTOBO error code and message. This makes it easy to separate business-level failures from HTTP transport issues (which continue to raise `httpx` exceptions). 【F:src/otobo/clients/otobo_client.py†L45-L87】【F:src/otobo/util/otobo_errors.py†L1-L7】

You can adjust the `max_retries` parameter when instantiating the client if you want to implement custom retry loops around calls. The class stores the value but leaves the retry strategy to your application, enabling integration with libraries like `tenacity` or bespoke retry logic. 【F:src/otobo/clients/otobo_client.py†L27-L38】

## Closing Notes

- All domain models are Pydantic models, giving you `.model_dump()` helpers and runtime validation of inputs before any network request is sent.
- Ticket articles automatically parse `CreateTime`/`ChangeTime` strings from the API into `datetime` objects where possible, simplifying downstream processing. 【F:src/otobo/mappers.py†L1-L89】
- Use the included CLI scripts under `otobo.scripts` as examples of how to wire the client into tooling and deployment automation.

Refer to the unit tests in `tests/unit/` for additional usage patterns and edge case handling.
