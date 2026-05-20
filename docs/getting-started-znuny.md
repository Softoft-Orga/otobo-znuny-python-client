# Getting Started with the Znuny Python SDK

Install the distribution and import the **Znuny-branded** namespace:

```bash
pip install znuny
```

```python
from znuny import ZnunyClient, BasicAuth, ClientConfig, TicketCreate, TicketOperation
```

## Configuration

```python
config = ClientConfig(
    base_url="https://your-znuny-server",
    webservice_name="PythonClientWebService",
    operation_url_map={
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.GET: "ticket-get",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.UPDATE: "ticket-update",
    },
)

client = ZnunyClient(config)
client.login(BasicAuth(user_login="agent1", password="secret"))
```

## CLI setup

On a Znuny host or inside its Docker container:

```bash
znuny-cli setup-system
```

Znuny uses the legacy `otrs.Console.pl` console path by default.

## Further reading

- [OTOBO SDK getting started](getting-started-otobo.md)
- [Migration from the combined client](migration.md)
