import asyncio
import json
import logging
import uuid
from http import HTTPMethod
from types import TracebackType
from typing import Any, Self, TypeVar
from urllib.parse import quote

from httpx import AsyncClient
from pydantic import BaseModel

from otobo_znuny_python_client.domain_models.basic_auth_model import BasicAuth
from otobo_znuny_python_client.domain_models.otobo_client_config import ClientConfig
from otobo_znuny_python_client.domain_models.ticket_models import Ticket, TicketCreate, TicketSearch, TicketUpdate
from otobo_znuny_python_client.domain_models.ticket_operation import TicketOperation
from otobo_znuny_python_client.mappers import (
    from_ws_ticket_detail,
    to_ws_auth,
    to_ws_ticket_create,
    to_ws_ticket_search,
    to_ws_ticket_update,
)
from otobo_znuny_python_client.models.request_models import WsTicketGetRequest
from otobo_znuny_python_client.models.request_models import (
    WsTicketMutationRequest,
)
from otobo_znuny_python_client.models.response_models import (
    WsTicketGetResponse,
    WsTicketResponse,
    WsTicketSearchResponse,
)
from otobo_znuny_python_client.util.otobo_errors import OTOBOError

T = TypeVar("T", bound=BaseModel)


class OTOBOZnunyClient:
    def __init__(self,
                 config: ClientConfig,
                 client: AsyncClient | None = None,
                 web_service_url_base="Webservice"):
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.webservice_name = config.webservice_name.strip("/")
        self.operation_map = config.operation_url_map
        self._web_service_url_base = (web_service_url_base or "").strip("/")
        self._logger = logging.getLogger(__name__)
        self._owns_client = client is None
        self._client: AsyncClient = client or AsyncClient(base_url=self.base_url)
        self._auth: BasicAuth | None = None
        parts = [p for p in [self._web_service_url_base, self.webservice_name] if p]
        self._ws_base_path = "/".join(quote(p, safe=":@$+,;=-._~()") for p in parts)

    def _build_url(self, endpoint_url: str, url_params: dict[str, Any] | None = None) -> str:
        """
        Build a URL path with optional parameter substitution.

        Args:
            endpoint_url: URL pattern with :param placeholders (e.g., "tickets/:TicketID")
            url_params: Dictionary of parameter values to substitute

        Returns:
            Complete URL path with base path and substituted parameters
        """
        url_params = url_params or {}
        for key, value in url_params.items():
            endpoint_url = endpoint_url.replace(f":{key}", str(value))

        ep = "/".join(quote(s, safe=":@$+,;=-._~()") for s in endpoint_url.strip("/").split("/"))
        return f"/{self._ws_base_path}/{ep}" if self._ws_base_path else f"/{ep}"

    def _extract_error(self, payload: Any) -> OTOBOError | None:
        if isinstance(payload, dict) and "Error" in payload:
            err = payload.get("Error") or {}
            return OTOBOError(str(err.get("ErrorCode", "")), str(err.get("ErrorMessage", "")))
        return None

    async def _send(
            self,
            method: HTTPMethod,
            operation: TicketOperation,
            response_model: type[T],
            data: dict[str, Any] | None = None,
            url_params: dict[str, Any] | None = None,
    ) -> T:
        if not self._auth:
            raise RuntimeError("Client is not authenticated")
        ws_auth = to_ws_auth(self._auth)
        endpoint_url = self.operation_map[operation]
        url = self._build_url(endpoint_url, url_params)
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

    async def get_ticket(self, ticket_id: int | str) -> Ticket:
        response: WsTicketGetResponse = await self._send(
            HTTPMethod.POST,
            TicketOperation.GET,
            WsTicketGetResponse,
            data=WsTicketGetRequest().model_dump(exclude_none=True, by_alias=True),
            url_params={"TicketID": ticket_id},
        )
        tickets = response.Ticket or []
        if len(tickets) != 1:
            raise RuntimeError(f"expected exactly one ticket, got {len(tickets)}")
        return from_ws_ticket_detail(
            tickets[0],
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

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                        tb: TracebackType | None) -> None:
        await self.aclose()
