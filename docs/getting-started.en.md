# Getting Started with the OTOBO Python Client

The OTOBO Python client provides an asynchronous interface to the OTOBO REST API. This guide shows how to install the
package and create a ticket.

## Installation

```bash
pip install otobo
```

## Configuration

```python
from otobo_znuny_python_client import OTOBOClient, OTOBOClientConfig, AuthData, TicketCreateParams, TicketCommon,
    ArticleDetail,

TicketOperation

config = OTOBOClientConfig(
    base_url="https://your-otobo-server/nph-genericinterface.pl",
    webservice_name="OTOBO",
    auth=AuthData(UserLogin="user1", Password="SecurePassword"),
    operation_url_map={
        TicketOperation.CREATE.value: "ticket",
        TicketOperation.SEARCH.value: "ticket/search",
    },
)

client = OTOBOClient(config)
```

## Create a Ticket

```python
payload = TicketCreateParams(
    Ticket=TicketCommon(
        Title="New Order",
        Queue="Sales",
        State="new",
        Priority="3 normal",
        CustomerUser="customer@example.com",
    ),
    Article=ArticleDetail(
        CommunicationChannel="Email",
        Charset="utf-8",
        Subject="Order",
        Body="Hello",
        MimeType="text/plain",
    ),
)

await client.create_ticket(payload)
```

## Further Reading

See the [project README on GitHub](https://github.com/Softoft-GmbH/otobo-znuny-python-client/blob/main/README.md)
for more features and examples.
