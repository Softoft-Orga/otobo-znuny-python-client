# otobo_client/client.py
import logging
# create TicketOperation Enum
from typing import Any, Dict, List, Optional, Type

import httpx
from pydantic import BaseModel

from client_config_models import TicketOperation, OTOBOClientConfig
from models.request_models import TicketSearchParams, TicketCreateParams, TicketHistoryParams, TicketUpdateParams, \
    TicketGetParams
from models.response_models import OTOBOTicketCreateResponse, OTOBOTicketGetResponse, \
    OTOBOTicketHistoryResponse, TicketUpdateResponse, TicketSearchResponse, FullTicketSearchResponse
from otobo_errors import OTOBOError
from util.http_method import HttpMethod


class OTOBOClient:
    def __init__(self, config: OTOBOClientConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.service = config.service
        self.auth = config.auth
        self._logger = logging.getLogger(__name__)

    async def _call[T: BaseModel](self,
                                  method: HttpMethod,
                                  op_key: TicketOperation,
                                  response_model: Type[T],
                                  data: Optional[Dict[str, Any]] = None,
                                  ) -> T:
        if op_key not in self.config.operations:
            raise RuntimeError(f"Operation '{op_key}' is not configured")
        endpoint = self.config.operations[op_key]
        url = f"{self.base_url}/Webservice/{self.service}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        payload: Dict[str, Any] = self.auth.model_dump(exclude_none=True)
        if data:
            payload.update(data)
        async with httpx.AsyncClient() as client:
            resp = await client.request(method.value, url, json=payload, headers=headers)
        json_response = resp.json()
        if "Error" in json_response:
            err = json_response["Error"]
            raise OTOBOError(err["ErrorCode"], err["ErrorMessage"])
        resp.raise_for_status()
        return response_model.model_validate(json_response)

    async def create_ticket(self, payload: TicketCreateParams) -> OTOBOTicketCreateResponse:
        return await self._call(HttpMethod.POST, TicketOperation.CREATE, OTOBOTicketCreateResponse,
                                data=payload.model_dump(exclude_none=True))

    async def get_ticket(self, params: TicketGetParams) -> OTOBOTicketGetResponse:
        return await self._call(HttpMethod.POST, TicketOperation.GET, OTOBOTicketGetResponse,
                                data=params.model_dump(exclude_none=True))

    async def update_ticket(self, payload: TicketUpdateParams) -> TicketUpdateResponse:
        return await self._call(HttpMethod.PUT, TicketOperation.UPDATE, TicketUpdateResponse,
                                data=payload.model_dump(exclude_none=True))

    async def search_tickets(self, query: TicketSearchParams) -> TicketSearchResponse:
        return await self._call(HttpMethod.POST, TicketOperation.SEARCH, TicketSearchResponse,
                                data=query.model_dump(exclude_none=True))

    async def get_ticket_history(self, payload: TicketHistoryParams) -> OTOBOTicketHistoryResponse:
        return await self._call(HttpMethod.POST, TicketOperation.HISTORY_GET, OTOBOTicketHistoryResponse,
                                data=payload.model_dump(exclude_none=True))

    async def search_and_get(self, query: TicketSearchParams) -> FullTicketSearchResponse:
        if TicketOperation.SEARCH not in self.config.operations or TicketOperation.GET not in self.config.operations:
            raise RuntimeError("Both 'TicketSearch' and 'TicketGet' must be configured for search_and_get")
        ids = (await self.search_tickets(query)).TicketID
        ticket_get_responses: List[OTOBOTicketGetResponse] = [await self.get_ticket(TicketGetParams(TicketID=i)) for i
                                                              in ids]
        return [ticket.Ticket for ticket in ticket_get_responses]
