import asyncio
import json
import logging
import random
import uuid
from http import HTTPMethod
from typing import Any, Iterable, Optional

import httpx
from httpx import AsyncClient
from pydantic import BaseModel, ValidationError

from otobo.domain_models.otobo_client_config import OTOBOClientConfig
from otobo.domain_models.ticket_operation import TicketOperation
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
    def __init__(self, config: OTOBOClientConfig, client: AsyncClient | None = None, max_retries: int = 2):
        self.config = config
        self._client = client or AsyncClient()
        self.base_url = config.base_url.rstrip("/")
        self.webservice_name = config.webservice_name
        self.auth = config.auth
        self.operation_map = config.operation_url_map
        self.max_retries = max_retries
        self._logger = logging.getLogger(__name__)

    def _build_url(self, endpoint_name: str) -> str:
        return f"{self.base_url}/Webservice/{self.webservice_name}/{endpoint_name}"


    def _extract_error(self, payload: Any) -> Optional[OTOBOError]:
        if isinstance(payload, dict) and "Error" in payload:
            err = payload.get("Error") or {}
            return OTOBOError(str(err.get("ErrorCode", "")), str(err.get("ErrorMessage", "")))
        return None

    async def _send[T: BaseModel](
            self,
            method: HTTPMethod,
            operation: TicketOperation,
            response_model: type[T],
            data: dict[str, Any] | None = None,
    ) -> T:
        endpoint_name = self.operation_map[operation]
        url = self._build_url(endpoint_name)
        request_id = uuid.uuid4().hex
        payload = (self.auth.model_dump(by_alias=True, exclude_none=True) if isinstance(self.auth, BaseModel) else dict(
            self.auth)) | (data or {})

        self._logger.debug(f"[{request_id}] {method.value} {url} payload_keys={list(payload.keys())}")
        resp = await self._client.request(
            str(method.value),
            url,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        text = resp.text
        self._logger.debug(f"[{request_id}] status={resp.status_code} length={len(text)}")

        try:
            body = resp.json()
        except json.JSONDecodeError:
            self._logger.error(f"[{request_id}] invalid JSON response: {text[:500]}")
            resp.raise_for_status()
            raise

        api_err = self._extract_error(body)
        if api_err:
            self._logger.error(f"[{request_id}] OTOBO error {api_err.code}: {api_err.message}")
            raise api_err

        resp.raise_for_status()
        try:
            return response_model.model_validate(body, strict=False)
        except ValidationError as e:
            self._logger.error(f"[{request_id}] response validation error: {e}")
            return response_model.model_construct(**body)

    async def create_ticket(self, request: TicketCreateRequest) -> TicketDetailOutput:
        response: TicketResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.CREATE,
            TicketResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        if response.Ticket is None:
            raise RuntimeError("create returned no Ticket")
        return response.Ticket

    async def get_ticket(self, request: TicketGetRequest) -> TicketDetailOutput:
        response: TicketGetResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.GET,
            TicketGetResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        tickets = response.Ticket or []
        if len(tickets) != 1:
            raise RuntimeError(f"expected exactly one ticket, got {len(tickets)}")
        return tickets[0]

    async def update_ticket(self, request: TicketUpdateRequest) -> TicketDetailOutput:
        response: TicketResponse = await self._send(
            HTTPMethod.PUT,
            TicketOperation.UPDATE,
            TicketResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        if response.Ticket is None:
            raise RuntimeError("update returned no Ticket")
        return response.Ticket

    async def search_tickets(self, request: TicketSearchRequest) -> list[int]:
        response: TicketSearchResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            TicketSearchResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        return response.TicketID or []

    async def search_and_get(self, request: TicketSearchRequest, max_tickets: int = 3, shuffle: bool = False) -> list[
        TicketDetailOutput]:
        ids = await self.search_tickets(request)
        if shuffle:
            random.shuffle(ids)
        tasks = [self.get_ticket(TicketGetRequest(TicketID=i)) for i in ids[:max_tickets]]
        return await asyncio.gather(*tasks)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()
