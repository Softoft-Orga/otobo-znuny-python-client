# Erste Schritte mit dem OTOBO Python Client

Der OTOBO Python Client stellt eine asynchrone Schnittstelle zur OTOBO REST API bereit. Diese Anleitung zeigt die Installation und das Anlegen eines Tickets.

## Installation

```bash
pip install otobo
```

## Konfiguration

```python
from otobo import OTOBOClient, OTOBOClientConfig, AuthData, TicketCreateParams, TicketCommon, ArticleDetail, TicketOperation

config = OTOBOClientConfig(
    base_url="https://dein-otobo-server/nph-genericinterface.pl",
    service="OTOBO",
    auth=AuthData(UserLogin="user1", Password="SicheresPasswort"),
    operations={
        TicketOperation.CREATE.value: "ticket",
        TicketOperation.SEARCH.value: "ticket/search",
    },
)

client = OTOBOClient(config)
```

## Ticket erstellen

```python
payload = TicketCreateParams(
    Ticket=TicketCommon(
        Title="Neue Bestellung",
        Queue="Vertrieb",
        State="neu",
        Priority="3 normal",
        CustomerUser="kunde@example.com",
    ),
    Article=ArticleDetail(
        CommunicationChannel="Email",
        Charset="utf-8",
        Subject="Bestellung",
        Body="Hallo",
        MimeType="text/plain",
    ),
)

await client.create_ticket(payload)
```

## Weiterführende Informationen

Weitere Funktionen und Beispiele finden sich im [Projekt-README](../README.md).
