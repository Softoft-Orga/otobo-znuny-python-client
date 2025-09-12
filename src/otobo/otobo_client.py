import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

import httpx
from httpx import AsyncClient
from pydantic import BaseModel, ValidationError

from .models.client_config_models import TicketOperation, OTOBOClientConfig
from .models.request_models import (
    TicketSearchParams,
    TicketUpdateParams,
    TicketGetParams,
)
from .models.response_models import (
    TicketUpdateResponse,
    TicketSearchResponse,
    TicketGetResponse, TicketCreateResponse,
)
from .models.ticket_models import TicketDetailOutput, TicketDetailInput
from .otobo_errors import OTOBOError
from http import HTTPMethod

class OTOBOClient:
    """
    Asynchronous client for interacting with the OTOBO ticketing system via its REST Webservice API.

    Args:
        config (OTOBOClientConfig): Configuration including base_url, service name, auth and operations mapping.
        client (httpx.AsyncClient, optional): Custom HTTP client instance.
         If not provided, a default AsyncClient is used.
    """

    def __init__(self, config: OTOBOClientConfig, client: httpx.AsyncClient = None):
        self._client = client or AsyncClient()
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.service = config.service
        self.auth = config.auth
        self._logger = logging.getLogger(__name__)

    def _build_url(self, endpoint: str) -> str:
        """
        Build the full URL for a given endpoint of the configured OTOBO service.

        Args:
            endpoint (str): Endpoint path defined in OTOBOClientConfig.operations.

        Returns:
            str: Fully qualified URL for the Webservice endpoint.
        """
        return f"{self.base_url}/Webservice/{self.service}/{endpoint}"

    def _check_operation_registered(self, op_key: TicketOperation) -> None:
        """
        Verify that the specified operation is registered in the client configuration.

        Args:
            op_key (TicketOperation): Operation enum key to check.

        Raises:
            RuntimeError: If the operation is not defined in config.operations.
        """
        if op_key not in self.config.operations:
            raise RuntimeError(f"Operation '{op_key}' is not configured in OTOBOClientConfig")

    def _check_response(self, response: Dict[str, Any]) -> None:
        """
        Inspect the JSON response for an error and raise if present.

        Args:
            response (Dict[str, Any]): Parsed JSON response from OTOBO.

        Raises:
            OTOBOError: If the response contains an 'Error' key with details.
        """
        if "Error" in response:
            err = response["Error"]
            raise OTOBOError(err["ErrorCode"], err["ErrorMessage"])

    async def _call[
    T: BaseModel
    ](
            self,
            method: HTTPMethod,
            op_key: TicketOperation,
            response_model: Type[T],
            data: Optional[Dict[str, Any]] = None,
    ) -> T:
        """
        Internal helper to perform an HTTP request to an OTOBO Webservice endpoint.

        Args:
            method (HttpMethod): HTTP method enum for the request.
            op_key (TicketOperation): Operation enum to determine URL path.
            response_model (Type[T]): Pydantic model for validating the response.
            data (Dict[str, Any], optional): Payload to send in the request body. Defaults to None.

        Returns:
            T: Validated response model instance.

        Raises:
            RuntimeError: If operation is not registered.
            OTOBOError: If the response JSON contains an error.
            httpx.HTTPError: For network or HTTP-level errors.
        """
        self._check_operation_registered(op_key)
        url = self._build_url(self.config.operations[op_key])
        headers = {'Content-Type': 'application/json'}
        payload: Dict[str, Any] = self.auth.model_dump(exclude_none=True) | (data or {})
        resp = await self._client.request(str(method.value), url, json=payload, headers=headers)
        json_response = resp.json()
        self._check_response(json_response)
        resp.raise_for_status()
        try:
            return response_model.model_validate(json_response)
        except ValidationError as e:
            self._logger.error("Response validation error: %s", e)
            return response_model.model_construct(**json_response)

    async def create_ticket(
            self, payload: TicketDetailInput
    ) -> TicketCreateResponse:
        """
        Create a new ticket in OTOBO.

        Args:
            payload (TicketCreateParams): Parameters for ticket creation.

        Returns:
            OTOBOTicketCreateResponse: Response model with created ticket details.
        """
        return await self._call(
            HTTPMethod.POST,
            TicketOperation.CREATE,
            TicketCreateResponse,
            data=payload.model_dump(exclude_none=True),
        )

    async def get_ticket(self, params: TicketGetParams) -> TicketDetailOutput:
        """
        Retrieve a single ticket by its ID.

        Args:
            params (TicketGetParams): Parameters containing TicketID.

        Returns:
            TicketGetResponse: Model containing exactly one Ticket object.

        Raises:
            AssertionError: If the response does not contain exactly one ticket.
        """
        otobo_ticket_get_response  = await self._call(
            HTTPMethod.POST,
            TicketOperation.GET,
            TicketGetResponse,
            data=params.model_dump(exclude_none=True),
        )
        tickets = otobo_ticket_get_response.Ticket
        assert len(tickets) == 1, "Expected exactly one ticket in the response"
        return tickets[0]

    async def update_ticket(
            self, payload: TicketUpdateParams
    ) -> TicketUpdateResponse:
        """
        Update an existing ticket's fields.

        Args:
            payload (TicketUpdateParams): Parameters including TicketID and update fields.

        Returns:
            TicketUpdateResponse: Response model with update result status.
        """
        return await self._call(
            HTTPMethod.PUT,
            TicketOperation.UPDATE,
            TicketUpdateResponse,
            data=payload.model_dump(exclude_none=True),
        )

    async def search_tickets(
            self, query: TicketSearchParams
    ) -> TicketSearchResponse:
        """
        Search for tickets matching given criteria.

        Args:
            query (TicketSearchParams): Search filters and options.

        Returns:
            TicketSearchResponse: Response model with list of matching TicketIDs.
        """
        return await self._call(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            TicketSearchResponse,
            data=query.model_dump(exclude_none=True),
        )

    async def search_and_get(
            self, query: TicketSearchParams
    ) -> list[TicketDetailOutput]:
        """
        Combine ticket search and retrieval in one call sequence.

        Performs a search to retrieve TicketIDs, then fetches each ticket's details.

        Args:
            query (TicketSearchParams): Search filters and options.

        Returns:
            FullTicketSearchResponse: List of Ticket objects matching the search criteria.

        Raises:
            RuntimeError: If SEARCH or GET operations are not configured in the client.
        """
        if (
                TicketOperation.SEARCH not in self.config.operations
                or TicketOperation.GET not in self.config.operations
        ):
            raise RuntimeError(
                "Both 'TicketSearch' and 'TicketGet' must be configured for search_and_get"
            )
        ids = (await self.search_tickets(query)).TicketID
        ticket_get_responses_tasks = [
            self.get_ticket(TicketGetParams(TicketID=i)) for i in ids
        ]
        return await asyncio.gather(*ticket_get_responses_tasks)
