# Getting Started with the OTOBO Python SDK

Install the distribution and import the **OTOBO-branded** namespace:

```bash
pip install otobo
```

```python
from otobo import OTOBOClient, BasicAuth, ClientConfig, TicketCreate, TicketOperation
```

## Configuration

```python
config = ClientConfig(
    base_url="https://your-otobo-server",
    webservice_name="PythonClientWebService",
    operation_url_map={
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.GET: "ticket-get",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.UPDATE: "ticket-update",
    },
)

client = OTOBOClient(config)
client.login(BasicAuth(user_login="agent1", password="secret"))
```

## Create a ticket

```python
import asyncio

from otobo import Article, IdName, TicketCreate


async def main() -> None:
    ticket = TicketCreate(
        title="New request",
        queue=IdName(name="Raw"),
        article=Article(subject="Hello", body="Ticket body"),
    )
    async with client:
        created = await client.create_ticket(ticket)
        print(created.id)


asyncio.run(main())
```

## CLI setup

On an OTOBO host or inside its Docker container:

```bash
otobo-cli setup-system
```

## Further reading

- [Znuny SDK getting started](getting-started-znuny.md)
- [Migration from the combined client](migration.md)
