from abc import abstractmethod, ABC
from datetime import datetime
from typing import Any, Optional, Self, Union

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class IdName(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Optional[int] = None
    name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        return s or None

    @model_validator(mode="after")
    def _require_one(self) -> Self:
        if self.id is None and self.name is None:
            raise ValueError("either id or name must be set")
        return self


class Article(BaseModel):
    from_addr: Optional[str] = None
    to_addr: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None
    changed_at: Optional[datetime] = None
    article_id: Optional[int] = None
    article_number: Optional[int] = None


class TicketBase(BaseModel, ABC):
    number: Optional[str] = None
    title: Optional[str] = None
    lock: Optional[IdName] = None
    queue: Optional[IdName] = None
    state: Optional[IdName] = None
    priority: Optional[IdName] = None
    type: Optional[IdName] = None
    owner: Optional[IdName] = None
    customer_id: Optional[str] = None
    customer_user: Optional[str] = None
    created_at: Optional[datetime] = None
    changed_at: Optional[datetime] = None
    dynamic_fields: dict[str, str] = {}

    @abstractmethod
    def get_articles(self) -> list[Article]:
        pass


class TicketCreate(TicketBase):
    article: Optional[Article] = None

    def get_articles(self) -> list[Article]:
        return [self.article] if self.article else []


class TicketUpdate(TicketBase):
    id: Optional[int] = None
    article: Optional[Article] = None

    def get_articles(self) -> list[Article]:
        return [self.article] if self.article else []


class Ticket(TicketBase):
    id: int
    articles: list[Article] = []

    def get_articles(self) -> list[Article]:
        return self.articles or []


class DynamicFieldFilter(BaseModel):
    field_name: str
    equals: Union[Any, list[Any], None] = None
    like: Optional[str] = None
    greater: Optional[Any] = None
    smaller: Optional[Any] = None


class TicketSearch(BaseModel):
    numbers: Optional[list[str]] = None
    titles: Optional[list[str]] = None
    queues: Optional[list[IdName]] = None
    states: Optional[list[IdName]] = None
    locks: Optional[list[IdName]] = None
    priorities: Optional[list[IdName]] = None
    types: Optional[list[IdName]] = None
    customer_users: Optional[list[str]] = None
    use_subqueues: bool = False
    limit: int = 50
    dynamic_fields: Optional[list[DynamicFieldFilter]] = None
