# conftest.py
import asyncio
import os
import re
from collections.abc import Generator

# tests/conftest.py (Ergänzung)
import mariadb
import pytest
from dotenv import load_dotenv

from otobo.clients.otobo_client import OTOBOZnunyClient
from otobo.domain_models.otobo_client_config import OTOBOClientConfig
from otobo.domain_models.basic_auth_model import BasicAuth
from otobo.domain_models.ticket_operation import TicketOperation
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def _safe_identifier(name: str) -> tuple[str, str | None]:
    if not re.fullmatch(r"[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)?", name):
        raise ValueError("Invalid table name")
    if "." in name:
        db, tbl = name.split(".", 1)
        return f"`{tbl}`", f"`{db}`"
    return f"`{name}`", None


def clear_table(
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        table: str,
) -> None:
    tbl, db_override = _safe_identifier(table)
    conn = mariadb.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database,
        autocommit=True,
    )
    try:
        cur = conn.cursor()
        if db_override:
            print(f"Clearing table {db_override}.{tbl}")
            cur.execute(f"DELETE FROM {db_override}.{tbl}")
        else:
            print(f"Clearing table {tbl}")
            cur.execute(f"DELETE FROM {tbl}")
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def clear_otobo_tables() -> None:
    load_dotenv(os.path.join(os.path.dirname(__file__), "e2e", "test_demo_env"))

    clear_table(
        host=os.environ["MARIADB_HOST"],
        port=int(os.environ["MARIADB_PORT"]),
        database=os.environ["MARIADB_DATABASE"],
        user=os.environ["MARIADB_USER"],
        password=os.environ["MARIADB_PASSWORD"],
        table="ticket",
    )

@pytest.fixture(scope="function")
async def open_ticket_ai_auth() -> BasicAuth:
    load_dotenv(os.path.join(os.path.dirname(__file__), "e2e", "test_demo_env"))

    user = os.environ["OTOBO_DEMO_USER"]
    password = os.environ["OTOBO_DEMO_PASSWORD"]
    return BasicAuth(UserLogin=user, Password=password)


@pytest.fixture(scope="function")
async def otobo_client(open_ticket_ai_client_config: OTOBOClientConfig) -> OTOBOZnunyClient:
    return OTOBOZnunyClient(config=open_ticket_ai_client_config)

@pytest.fixture(scope="function")
async def security_user_client(security_user_client_config) -> OTOBOZnunyClient:
    return OTOBOZnunyClient(config=security_user_client_config)

def _create_config(auth: BasicAuth) -> OTOBOClientConfig:
    load_dotenv(os.path.join(os.path.dirname(__file__), "e2e", "test_demo_env"))

    base_url = os.environ["OTOBO_BASE_URL"]
    service = os.environ["OTOBO_SERVICE"]
    operations: dict[TicketOperation, str] = {
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.GET: "ticket-get",
        TicketOperation.UPDATE: "ticket-update",
    }
    config = OTOBOClientConfig(
        base_url=base_url,
        webservice_name=service,
        auth=auth,
        operation_url_map=operations,
    )
    return config

@pytest.fixture(scope="function")
async def open_ticket_ai_client_config(open_ticket_ai_auth) -> OTOBOClientConfig:
    return _create_config(auth=open_ticket_ai_auth)

@pytest.fixture(scope="function")
async def security_user_client_config() -> OTOBOClientConfig:
    load_dotenv(os.path.join(os.path.dirname(__file__), "e2e", "test_demo_env"))

    user = "security_test"
    password = "qiTSn3KmTFZWgoAyUKa84UkB"
    auth = BasicAuth(UserLogin=user, Password=password)
    return _create_config(auth=auth)