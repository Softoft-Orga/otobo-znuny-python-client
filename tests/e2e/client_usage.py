#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
import time
from typing import Dict, Any, Optional

# Add this import
from dotenv import load_dotenv

from models.ticket_models import TicketBase
from otobo import (
    OTOBOClient,
    OTOBOClientConfig,
    TicketOperation,
    TicketSearchRequest,
    TicketGetRequest,
    TicketUpdateRequest,
)
from otobo.models.request_models import AuthData

# --- Setup Logging ---
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("integration_demo")


class OTOBOTestExecutor:
    """
    A class to encapsulate the OTOBO client and the testing flow.
    """

    def __init__(self, config: OTOBOClientConfig):
        self.client = OTOBOClient(config)
        self.ticket_id: Optional[int] = None
        self.ticket_number: Optional[str] = None

    async def create_ticket(self) -> None:
        """
        Creates a new ticket.
        """
        logger.info("Creating a new ticket...")
        ts = int(time.time())
        title = f"TestTicket {ts}"
        payload_create = TicketCreateParams(
            Ticket=TicketCommon(
                Title=title,
                Queue="Raw",
                State="new",
                Priority="3 normal",
                Type="Incident",
                CustomerUser="customer@localhost.de",
            ),
            Article=ArticleDetail(
                CommunicationChannel="Email",
                Charset="utf-8",
                Subject="Integration Test",
                Body="This is a test",
                MimeType="text/plain",
            ),
        )
        res_create = await self.client.create_ticket(payload_create)
        logger.debug("Create Ticket Response: %s", res_create)
        self.ticket_number = res_create.TicketNumber
        self.ticket_id = int(res_create.TicketID)
        logger.info("Created ticket_number: %s", self.ticket_number)

    async def search_ticket(self) -> None:
        """
        Searches for the created ticket.
        """
        logger.info("Searching for the ticket...")
        query_search = TicketSearchRequest(Queues=["Raw"])
        ticket_search_response = await self.client.search_tickets(query_search)
        logger.info("Search returned IDs: %s", ticket_search_response)
        # Add a simple check
        assert self.ticket_id in ticket_search_response.TicketID, "The created ticket was not found"

    async def get_ticket_details(self) -> None:
        """
        Retrieves the details of the created ticket.
        """
        logger.info("Retrieving ticket details...")
        res_get = await self.client.get_ticket(
            TicketGetRequest(TicketID=self.ticket_id, AllArticles=1)
        )
        logger.info("Ticket Data: %s", res_get)

    async def update_ticket(self) -> None:
        """
        Updates the state of the created ticket to 'closed'.
        """
        logger.info("Updating the ticket state to 'closed'...")
        payload_update = TicketUpdateRequest(
            TicketID=self.ticket_id,
            Ticket=TicketBase(
                Queue="Junk"
            ),
        )
        res_update = await self.client.update_ticket(payload_update)
        logger.info("Updated Ticket Response: %s", res_update)
        logger.info("Updated TicketID: %s", res_update.TicketID)


    async def search_and_get_combined(self) -> None:
        """
        Performs a combined search and get operation.
        """
        logger.info("Performing search_and_get...")
        query_search = TicketSearchRequest(Queues=["test"])
        combined = await self.client.search_and_get(query_search)
        if combined and isinstance(combined, list):
            logger.info("search_and_get result %s", combined)
        else:
            logger.error("search_and_get did not return expected data")
            sys.exit(1)


    async def run_full_test_flow(self) -> None:
        """
        Runs the full testing flow in the correct order.
        """
        await self.create_ticket()
        await self.search_ticket()
        await self.get_ticket_details()
        await self.update_ticket()
        await self.search_and_get_combined()
        logger.info("Integration demo complete successfully.")


def get_config_from_env() -> OTOBOClientConfig:
    """
    Creates an OTOBOClientConfig from environment variables.
    """
    base_url = os.environ.get("OTOBO_BASE_URL")
    service = os.environ.get("OTOBO_SERVICE")
    user = os.environ.get("OTOBO_TEST_USER")
    password = os.environ.get("OTOBO_TEST_PASSWORD")

    if not all([base_url, service, user, password]):
        logger.error(
            "Please set the OTOBO_BASE_URL, OTOBO_SERVICE, OTOBO_USER, and OTOBO_PASSWORD environment variables.")
        sys.exit(1)

    operations: dict[TicketOperation, str] = {
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.GET: "ticket-get",
        TicketOperation.UPDATE: "ticket-update",
    }

    auth = AuthData(UserLogin=user, Password=password)
    return OTOBOClientConfig(
        base_url=base_url,
        service=service,
        auth=auth,
        operations=operations,
    )


async def main():
    """
    Main function to run the OTOBO test executor.
    """
    # Load environment variables from .env file
    load_dotenv()

    otobo_client_config = get_config_from_env()
    executor = OTOBOTestExecutor(otobo_client_config)
    await executor.run_full_test_flow()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error("An error occurred: %s", e)
        sys.exit(1)