import asyncio
import json
import logging
import uuid
from http import HTTPMethod
from types import TracebackType
from typing import Any, Optional, Self, TypeVar, Union

from httpx import AsyncClient
from pydantic import BaseModel

from otobo_znuny.domain_models.basic_auth_model import BasicAuth
from otobo_znuny.mappers import to_ws_ticket_create, from_ws_ticket_detail, to_ws_auth, to_ws_ticket_get, \
    to_ws_ticket_update, \
    to_ws_ticket_search
from otobo_znuny.domain_models.otobo_client_config import ClientConfig
from otobo_znuny.domain_models.ticket_models import TicketSearch, TicketUpdate, TicketCreate, Ticket
from otobo_znuny.domain_models.ticket_operation import TicketOperation
from otobo_znuny.models.request_models import (
    WsTicketMutationRequest,
)
from otobo_znuny.models.response_models import (
    WsTicketSearchResponse,
    WsTicketGetResponse,
    WsTicketResponse,
)
from otobo_znuny.util.otobo_errors import OTOBOError


class OTOBOZnunyClient:
    def __init__(self, config: ClientConfig, client: Optional[AsyncClient] = None, max_retries: int = 2):
        self.config = config
        self._client: AsyncClient = client or AsyncClient()
        self.base_url = config.base_url.rstrip("/")
        self.webservice_name = config.webservice_name
        self._auth: Optional[BasicAuth] = None
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

    T = TypeVar('T', bound=BaseModel)

    async def _send(
            self,
            method: HTTPMethod,
            operation: TicketOperation,
            response_model: type[T],
            data: Optional[dict[str, Any]] = None,
    ) -> T:
        if not self._auth:
            raise RuntimeError("Client is not authenticated")
        ws_auth = to_ws_auth(self._auth)
        endpoint_name = self.operation_map[operation]
        url = self._build_url(endpoint_name)
        request_id = uuid.uuid4().hex
        payload = ws_auth.model_dump(by_alias=True, exclude_none=True, with_secrets=True) | (data or {})

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
        except json.JSONDecodeError as e:
            self._logger.error(f"[{request_id}] invalid JSON response: {text[:500]}")
            raise e

        api_err = self._extract_error(body)
        if api_err:
            self._logger.error(f"[{request_id}] OTOBO error {api_err.code}: {api_err.message}")
            raise api_err

        resp.raise_for_status()
        return response_model.model_validate(body, strict=False)

    def login(self, auth: BasicAuth):
        self._auth = auth

    def logout(self):
        self._auth = None

    async def create_ticket(self, ticket: TicketCreate) -> Ticket:
        request: WsTicketMutationRequest = to_ws_ticket_create(ticket)
        response: WsTicketResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.CREATE,
            WsTicketResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        if response.Ticket is None:
            raise RuntimeError("create returned no Ticket")
        return from_ws_ticket_detail(response.Ticket)

    async def get_ticket(self, ticket_id: Union[int, str]) -> Ticket:
        request = to_ws_ticket_get(int(ticket_id))
        response: WsTicketGetResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.GET,
            WsTicketGetResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        tickets = response.Ticket or []
        if len(tickets) != 1:
            raise RuntimeError(f"expected exactly one ticket, got {len(tickets)}")
        return from_ws_ticket_detail(
            tickets[0]
        )

    async def update_ticket(self, ticket: TicketUpdate) -> Ticket:
        request = to_ws_ticket_update(ticket)
        response: WsTicketResponse = await self._send(
            HTTPMethod.PUT,
            TicketOperation.UPDATE,
            WsTicketResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        if response.Ticket is None:
            raise RuntimeError("update returned no Ticket")
        return from_ws_ticket_detail(response.Ticket)

    async def search_tickets(self, ticket_search: TicketSearch) -> list[int]:
        request = to_ws_ticket_search(ticket_search)
        response: WsTicketSearchResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.SEARCH,
            WsTicketSearchResponse,
            data=request.model_dump(exclude_none=True, by_alias=True),
        )
        return response.TicketID or []

    async def search_and_get(self, ticket_search: TicketSearch) -> list[Ticket]:
        ids = await self.search_tickets(ticket_search)
        tasks = [self.get_ticket(i) for i in ids]
        return await asyncio.gather(*tasks)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Optional[type[BaseException]], exc: Optional[BaseException],
                        tb: Optional[TracebackType]) -> None:
        await self.aclose()
