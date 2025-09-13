import asyncio
import logging
from typing import Any, Dict, List, Optional, Type, Union, Iterable

import httpx
from httpx import AsyncClient
from pydantic import BaseModel, ValidationError

"""Asynchronous client implementation for the OTOBO REST API."""

from otobo.models.client_config_models import TicketOperation, OTOBOClientConfig
from otobo.models.request_models import (
    TicketSearchRequest,
    TicketUpdateRequest,
    TicketGetRequest,
    TicketCreateRequest,
)
from otobo.models.response_models import (
    TicketSearchResponse,
    TicketGetResponse,
    TicketResponse,
)
from otobo.models.ticket_models import TicketDetailOutput
from otobo.util.otobo_errors import OTOBOError
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

    def _check_operation_registered(
            self,
            op_keys: Union[TicketOperation, Iterable[TicketOperation]]
    ) -> None:
        if isinstance(op_keys, (list, tuple, set)):
            missing = [op for op in op_keys if op not in self.config.operations]
            if missing:
                raise RuntimeError(f"Operations not configured in OTOBOClientConfig: {missing}")
        else:
            if op_keys not in self.config.operations:
                raise RuntimeError(f"Operation '{op_keys}' is not configured in OTOBOClientConfig")

    def _check_response(self, response: httpx.Response) -> None:
        """
        Inspect the JSON response for an error and raise if present.

        Args:
            response (Dict[str, Any]): Parsed JSON response from OTOBO.

        Raises:
            OTOBOError: If the response contains an 'Error' key with details.
        """
        response_json = response.json()
        if "Error" in response_json:
            err = response_json["Error"]
            raise OTOBOError(err.get("ErrorCode", ""), err.get("ErrorMessage", ""))
        response.raise_for_status()

    async def _request[
    T: BaseModel
    ](
            self,
            http_method: HTTPMethod,
            ticket_operation: TicketOperation,
            response_model: type[T],
            data: Optional[dict[str, Any]] = None,
    ) -> T:
        """
        Internal helper to perform an HTTP request to an OTOBO Webservice endpoint.

        Args:
            http_method (HttpMethod): HTTP method enum for the request.
            ticket_operation (TicketOperation): Operation enum to determine URL path.
            response_model (Type[T]): Pydantic model for validating the response.
            data (Dict[str, Any], optional): Payload to send in the request body. Defaults to None.

        Returns:
            T: Validated response model instance.

        Raises:
            RuntimeError: If operation is not registered.
            OTOBOError: If the response JSON contains an error.
            httpx.HTTPError: For network or HTTP-level errors.
        """
        self._check_operation_registered(ticket_operation)
        url = self._build_url(self.config.operations[ticket_operation])
        payload: dict[str, Any] = self.auth.model_dump(exclude_none=True) | (data or {})
        resp = await self._client.request(str(http_method.value), url, json=payload,
                                          headers={'Content-Type': 'application/json'})
        self._check_response(resp)
        try:
            return response_model.model_validate(resp.json())
        except ValidationError as e:
            self._logger.error("Response validation error: %s", e)
            return response_model.model_construct(**(resp.json()))

    async def create_ticket(
            self, payload: TicketCreateRequest
    ) -> TicketDetailOutput:
        """
        Create a new ticket in OTOBO.

        Args:
            payload (TicketCreateParams): Parameters for ticket creation.

        Returns:
            OTOBOTicketCreateResponse: Response model with created ticket details.
        """
        response: TicketResponse = await self._request(
            HTTPMethod.POST,
            TicketOperation.CREATE,
            TicketResponse,
            data=payload.model_dump(exclude_none=True),
        )

        return response.Ticket

    async def get_ticket(self, params: TicketGetRequest) -> TicketDetailOutput:
        """
        Retrieve a single ticket by its ID.

        Args:
            params (TicketGetRequest): Parameters containing TicketID.

        Returns:
            TicketGetResponse: Model containing exactly one Ticket object.

        Raises:
            AssertionError: If the response does not contain exactly one ticket.
        """
        otobo_ticket_get_response = await self._request(
            HTTPMethod.POST,
            TicketOperation.GET,
            TicketGetResponse,
            data=params.model_dump(exclude_none=True),
        )
        tickets = otobo_ticket_get_response.Ticket
        assert len(tickets) == 1, "Expected exactly one ticket in the response"
        return tickets[0]

    async def update_ticket(
            self, payload: TicketUpdateRequest
    ) -> TicketDetailOutput:
        """
        Update an existing ticket's fields.

        Args:
            payload (TicketUpdateRequest): Parameters including TicketID and update fields.

        Returns:
            TicketUpdateResponse: Response model with update result status.
        """
        response: TicketResponse = await self._request(
            HTTPMethod.PUT,
            TicketOperation.UPDATE,
            TicketResponse,
            data=payload.model_dump(exclude_none=True),
        )
        if response.Ticket is not None:
            return response.Ticket
        raise RuntimeError("Update operation did not return updated ticket details")

    async def search_tickets(
            self, query: TicketSearchRequest
    ) -> list[int]:
        """
        Search for tickets matching given criteria.

        Args:
            query (TicketSearchRequest): Search filters and options.

        Returns:
            List[int]: List of TicketIDs matching the search criteria.
        """
        response: TicketSearchResponse = await self._request(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            TicketSearchResponse,
            data=query.model_dump(exclude_none=True),
        )
        return response.TicketIDs

    async def search_and_get(
            self, query: TicketSearchRequest
    ) -> list[TicketDetailOutput]:
        """
        Combine ticket search and retrieval in one call sequence.
        Performs a search to retrieve TicketIDs, then fetches each ticket's details.

        Args:
            query (TicketSearchRequest): Search filters and options.

        Returns:
            FullTicketSearchResponse: List of Ticket objects matching the search criteria.

        Raises:
            RuntimeError: If SEARCH or GET operations arent configured in the client.
        """
        self._check_operation_registered([TicketOperation.SEARCH, TicketOperation.GET])
        ticket_get_responses_tasks = [
            self.get_ticket(TicketGetRequest(TicketID=i)) for i in await self.search_tickets(query)
        ]
        return await asyncio.gather(*ticket_get_responses_tasks)
