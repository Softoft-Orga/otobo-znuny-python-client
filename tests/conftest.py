# conftest.py
import asyncio
import os
import re

# tests/conftest.py (Ergänzung)
import mariadb
import pytest
from dotenv import load_dotenv

from otobo import OTOBOClientConfig, OTOBOClient
from otobo.domain_models.basic_auth_model import BasicAuth
from otobo.domain_models.ticket_operation import TicketOperation
@pytest.fixture(scope="session")
def event_loop():
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
def clear_otobo_tables():
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
async def otobo_client() -> OTOBOClient:
    load_dotenv(os.path.join(os.path.dirname(__file__), "e2e", "test_demo_env"))

    base_url = os.environ["OTOBO_BASE_URL"]
    service = os.environ["OTOBO_SERVICE"]
    user = os.environ["OTOBO_DEMO_USER"]
    password = os.environ["OTOBO_DEMO_PASSWORD"]
    print(user, password, base_url, service)
    operations: dict[TicketOperation, str] = {
        TicketOperation.CREATE: "ticket-create",
        TicketOperation.SEARCH: "ticket-search",
        TicketOperation.GET: "ticket-get",
        TicketOperation.UPDATE: "ticket-update",
    }
    auth = BasicAuth(UserLogin=user, Password=password)
    print(auth)
    config = OTOBOClientConfig(
        base_url=base_url,
        webservice_name=service,
        auth=auth,
        operation_url_map=operations,
    )
    return OTOBOClient(config=config)
