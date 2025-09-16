from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class IdName(BaseModel):
    id: int | None = None
    name: str | None = None

class Article(BaseModel):
    from_addr: str | None = None
    to_addr: str | None = None
    subject: str | None = None
    body: str | None = None
    content_type: str | None = None
    created_at: datetime | None = None
    changed_at: datetime | None = None
    article_id: int | None = None
    article_number: int | None = None

class Ticket(BaseModel):
    id: int | None = None
    number: str | None = None
    title: str | None = None
    queue: IdName | None = None
    state: IdName | None = None
    priority: IdName | None = None
    type: IdName | None = None
    owner: IdName | None = None
    customer_id: str | None = None
    customer_user: str | None = None
    created_at: datetime | None = None
    changed_at: datetime | None = None
    articles: list[Article] = Field(default_factory=list)

class TicketSearch(BaseModel):
    numbers: list[str] | None = None
    titles: list[str] | None = None
    queues: list[IdName] | None = None
    states: list[IdName] | None = None
    priorities: list[IdName] | None = None
    types: list[IdName] | None = None
    customer_users: list[str] | None = None
    use_subqueues: bool = False
    limit: int = 50
