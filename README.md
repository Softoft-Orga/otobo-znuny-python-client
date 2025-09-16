# Python OTOBO Client Library

## Links
- [Github Repo](https://github.com/Softoft/otobo-python-client)
- [Pypi Package](https://pypi.org/project/otobo/)
An asynchronous Python client for interacting with the OTOBO REST API. Built with `httpx` and `pydantic` for type safety
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

[OTOBO](https://pypi.org/project/otobo/) is available on PyPI and can be installed using pip:
Install from PyPI:

```bash
pip install otobo
```

## Quickstart

### Setup OTOBO Webservices:


````bash
# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install otobo
otobo setup

# Update later
uv tool upgrade otobo

````

Create a new web service in OTOBO with the following configuration:

````yaml
---
Debugger:
  DebugThreshold: debug
  TestMode: '0'
Description: ''
FrameworkVersion: 11.0.5
Provider:
  Operation:
    session-create:
      Description: ''
      IncludeTicketData: '0'
      MappingInbound:
        Type: Simple
      MappingOutbound:
        Type: Simple
      Type: Session::SessionCreate
    ticket-create:
      Description: ''
      IncludeTicketData: '1'
      MappingInbound:
        Type: Simple
      MappingOutbound:
        Type: Simple
      Type: Ticket::TicketCreate
    ticket-get:
      Description: ''
      IncludeTicketData: '0'
      MappingInbound:
        Config:
          KeyMapDefault:
            MapTo: ''
            MapType: Keep
          ValueMapDefault:
            MapTo: ''
            MapType: Keep
        Type: Simple
      MappingOutbound:
        Type: Simple
      Type: Ticket::TicketGet
    ticket-history-get:
      Description: ''
      IncludeTicketData: '0'
      MappingInbound:
        Type: Simple
      MappingOutbound:
        Type: Simple
      Type: Ticket::TicketHistoryGet
    ticket-search:
      Description: ''
      IncludeTicketData: '0'
      MappingInbound:
        Type: Simple
      MappingOutbound:
        Type: Simple
      Type: Ticket::TicketSearch
    ticket-update:
      Description: ''
      IncludeTicketData: '1'
      MappingInbound:
        Type: Simple
      MappingOutbound:
        Type: Simple
      Type: Ticket::TicketUpdate
  Transport:
    Config:
      AdditionalHeaders: ~
      KeepAlive: '1'
      MaxLength: '16000'
      RouteOperationMapping:
        session-create:
          RequestMethod:
            - HEAD
            - OPTIONS
            - PATCH
            - POST
            - PUT
          Route: /session
        ticket-create:
          RequestMethod:
            - HEAD
            - OPTIONS
            - POST
          Route: /ticket
        ticket-get:
          RequestMethod:
            - HEAD
            - OPTIONS
            - POST
          Route: /ticket/get
        ticket-history-get:
          RequestMethod:
            - HEAD
            - OPTIONS
            - POST
          Route: /ticket/history
        ticket-search:
          RequestMethod:
            - HEAD
            - OPTIONS
            - POST
          Route: /ticket/search
        ticket-update:
          RequestMethod:
            - HEAD
            - OPTIONS
            - PATCH
            - PUT
          Route: /ticket
    Type: HTTP::REST
RemoteSystem: ''
Requester:
  Transport:
    Type: HTTP::REST
````
### Create a new Agent

Create a new Otobo Agent with a secure password and give it the permissions needed for the thing you want to accomplish.


### 1. Configure the client

```python
from otobo import TicketOperation, OTOBOClientConfig
from otobo import AuthData

config = OTOBOClientConfig(
  base_url="https://your-otobo-server/nph-genericinterface.pl",
  webservice_name="OTOBO",
  auth=AuthData(UserLogin="user1", Password="SecurePassword"),
  operation_url_map={
    TicketOperation.CREATE.value: "ticket",
    TicketOperation.SEARCH.value: "ticket/search",
    TicketOperation.GET.value: "ticket/get",
    TicketOperation.UPDATE.value: "ticket",
    TicketOperation.HISTORY_GET.value: "ticket/history",
  }
)
```

### 2. Initialize the client

```python
import logging
from otobo import OTOBOClient

logging.basicConfig(level=logging.INFO)


client = OTOBOClient(config)
```

### 3. Create a ticket

```python
from otobo import (TicketOperation, OTOBOClientConfig, AuthData, TicketSearchRequest, TicketCreateParams,
                   TicketHistoryParams, TicketUpdateRequest,
                   TicketGetRequest, OTOBOClient, OTOBOTicketCreateResponse)

payload = TicketCreateParams(
  Ticket={
    "Title": "New Order",
    "Queue": "Sales",
    "State": "new",
    "Priority": "3 normal",
    "CustomerUser": "customer@example.com"
  },
  Article={
    "Subject": "Product Inquiry",
    "Body": "Please send pricing details...",
    "MimeType": "text/plain"
  }
)

response: OTOBOTicketCreateResponse = await client.create_ticket(payload)
print(response.TicketID, response.TicketNumber)
```

### 4. Search and retrieve tickets

```python
from otobo import TicketSearchRequest, TicketGetRequest

search_params = TicketSearchRequest(Title="%Order%")
search_res = await client.search_tickets(search_params)
ids = search_res.TicketID

for ticket_id in ids:
  get_params = TicketGetRequest(TicketID=ticket_id, AllArticles=1)
  details = await client.get_ticket(get_params)
  print(details.Ticket[0])
```

### 5. Update a ticket

```python
from otobo import TicketUpdateRequest

update_params = TicketUpdateRequest(
    TicketID=response.TicketID,
    Ticket={"State": "closed"}
)
await client.update_ticket(update_params)
```

### 6. Get ticket history

```python
from otobo import TicketHistoryParams

history_params = TicketHistoryParams(TicketID=str(response.TicketID))
history_res = await client.get_ticket_history(history_params)
print(history_res.History)
```

### 7. Combined search and get

```python
from otobo import FullTicketSearchResponse

full_res: FullTicketSearchResponse = await client.search_and_get(search_params)
```

## License

MIT © Softoft, Tobias A. Bueck
