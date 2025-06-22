#!/usr/bin/env python3
import logging
import time
import sys

from client_config_models import TicketOperation, OTOBOClientConfig
from models.request_models import AuthData, TicketSearchParams, TicketCreateParams, TicketHistoryParams, TicketUpdateParams, \
    TicketGetParams
from otobo.otobo_client import (
    OTOBOClient
)


async def main():
    # --- Configuration ---
    BASE_URL = "http://18.193.56.84/otobo/nph-genericinterface.pl"
    SERVICE = "OTOBO"
    USER = "root@localhost"
    PASSWORD = "1234"
    OPERATIONS = {
        TicketOperation.CREATE.value: "ticket",
        TicketOperation.SEARCH.value: "ticket/search",
        TicketOperation.GET.value: "ticket/get",
        TicketOperation.UPDATE.value: "ticket",
        TicketOperation.HISTORY_GET.value: "ticket/history",
    }

    # --- Setup Logging ---
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger = logging.getLogger("integration_demo")

    # --- Initialize Client ---
    auth = AuthData(UserLogin=USER, Password=PASSWORD)
    config = OTOBOClientConfig(
        base_url=BASE_URL,
        service=SERVICE,
        auth=auth,
        operations=OPERATIONS
    )
    client = OTOBOClient(config)

    # --- Helper to exit on error ---

    # --- 1. Create Ticket ---
    logger.info("Creating a new ticket...")
    ts = int(time.time())
    title = f"TestTicket {ts}"
    payload_create = TicketCreateParams(
        Ticket={
            "Title": title,
            "Queue": "Raw",
            "State": "new",
            "Priority": "3 normal",
            "CustomerUser": "customer@localhost.de",
        },
        Article={
            "CommunicationChannel": "Email",
            "Charset": "utf-8",
            "Subject": "Integration Test",
            "Body": "This is a test",
            "MimeType": "text/plain"
        }
    )
    res_create = await client.create_ticket(payload_create)
    logger.debug("Create Ticket Response: %s", res_create)
    ticket_number = res_create.TicketNumber
    logger.info("Created ticket_number: %s", ticket_number)

    # --- 2. Search Ticket ---
    logger.info("Searching for the ticket...")
    query_search = TicketSearchParams(QueueIDs=[1])
    ticket_search_response = await client.search_tickets(query_search)
    logger.info("Search returned IDs: %s", ticket_search_response)

    # --- 3. Get Ticket Details ---
    logger.info("Retrieving ticket details...")
    res_get = await client.get_ticket(TicketGetParams(TicketID=ticket_search_response.TicketID[0], AllArticles=1))
    logger.info("Ticket Data: %s", res_get)

    # --- 4. Update Ticket ---
    logger.info("Updating the ticket state to 'closed'...")
    payload_update = TicketUpdateParams(
        TicketID=ticket_search_response.TicketID[0],
        Ticket={"State": "closed successful"}
    )
    res_update = await client.update_ticket(payload_update)
    logger.info("Updated Ticket Response: %s", res_update)

    logger.info("Updated TicketID: %s", res_update.TicketID)

    # --- 5. Get Ticket TicketHistoryModel ---
    logger.info("Retrieving ticket history...")
    payload_history = TicketHistoryParams(TicketID=str(ticket_search_response.TicketID[0]))
    res_history = await client.get_ticket_history(payload_history)
    logger.info("Ticket TicketHistoryModel Data: %s", res_history)
    logger.info("TicketHistoryModel Entries: %s", res_history.TicketHistory)

    # --- 6. Search and Get Combined ---
    logger.info("Performing search_and_get...")
    combined = await client.search_and_get(query_search)
    if combined and isinstance(combined, list):
        logger.info("search_and_get result %s", combined)
    else:
        logger.error("search_and_get did not return expected data")
        sys.exit(1)

    logger.info("Integration demo complete successfully.")


if __name__ == '__main__':
    import asyncio

    try:
        asyncio.run(main())
    except Exception as e:
        logging.error("An error occurred: %s", e)
        sys.exit(1)