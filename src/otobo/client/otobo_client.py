import asyncio
import logging
import random
from http import HTTPMethod
from typing import Any, Dict, Optional, Union, Iterable

import httpx
from httpx import AsyncClient
from pydantic import BaseModel, ValidationError

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


class OTOBOClient:
    def __init__(self, config: OTOBOClientConfig, client: httpx.AsyncClient = None):
        self._client = client or AsyncClient()
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.service = config.service
        self.auth = config.auth
        self._logger = logging.getLogger(__name__)

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}/Webservice/{self.service}/{endpoint}"

    def _check_operation_registered(
            self,
            op_keys: Union[TicketOperation, Iterable[TicketOperation]]
    ) -> None:
        op_keys = op_keys if isinstance(op_keys, Iterable) else [op_keys]
        missing = [op for op in op_keys if op not in self.config.operations]
        if missing:
            raise RuntimeError(f"Operations not configured in OTOBOClientConfig: {missing}")
        if op_keys not in self.config.operations:
            raise RuntimeError(f"Operation '{op_keys}' is not configured in OTOBOClientConfig")

    def _check_response(self, response: httpx.Response) -> None:
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
        self._check_operation_registered(ticket_operation)
        url = self._build_url(self.config.operations[ticket_operation])
        payload: dict[str, Any] = self.auth.model_dump(exclude_none=True) | (data or {})
        resp = await self._client.request(str(http_method.value), url, json=payload,
                                          headers={'Content-Type': 'application/json'})
        self._check_response(resp)
        try:
            return response_model.model_validate(resp.json(), strict=False)
        except ValidationError as e:
            self._logger.error("Response validation error: %s", e)
            return response_model.model_construct(**(resp.json()))

    async def create_ticket(
            self, payload: TicketCreateRequest
    ) -> TicketDetailOutput:
        response: TicketResponse = await self._request(
            HTTPMethod.POST,
            TicketOperation.CREATE,
            TicketResponse,
            data=payload.model_dump(exclude_none=True),
        )

        return response.Ticket

    async def get_ticket(self, params: TicketGetRequest) -> TicketDetailOutput:
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

        response: TicketSearchResponse = await self._request(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            TicketSearchResponse,
            data=query.model_dump(exclude_none=True),
        )
        if response.TicketID:
            return response.TicketID
        else:
            return []

    async def search_and_get(
            self, query: TicketSearchRequest, max_tickets: int = 3, shuffle: bool = False
    ) -> list[TicketDetailOutput]:
        self._check_operation_registered([TicketOperation.SEARCH, TicketOperation.GET])

        ticket_ids = await self.search_tickets(query)
        if shuffle:
            random.shuffle(ticket_ids)

        ticket_get_responses_tasks = [
            self.get_ticket(TicketGetRequest(TicketID=i)) for i in ticket_ids[:max_tickets]
        ]
        return await asyncio.gather(*ticket_get_responses_tasks)
