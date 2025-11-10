from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class IdName(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: int | None = None
    name: str | None = None

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, v: str | None) -> str | None:
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
    from_addr: str | None = None
    to_addr: str | None = None
    subject: str | None = None
    body: str | None = None
    content_type: str | None = None
    created_at: datetime | None = None
    changed_at: datetime | None = None
    article_id: int | None = None
    article_number: int | None = None


class TicketBase(BaseModel, ABC):
    number: str | None = None
    title: str | None = None
    lock: IdName | None = None
    queue: IdName | None = None
    state: IdName | None = None
    priority: IdName | None = None
    type: IdName | None = None
    owner: IdName | None = None
    customer_id: str | None = None
    customer_user: str | None = None
    created_at: datetime | None = None
    changed_at: datetime | None = None
    dynamic_fields: dict[str, str] = {}

    @abstractmethod
    def get_articles(self) -> list[Article]:
        pass


class TicketCreate(TicketBase):
    article: Article | None = None

    def get_articles(self) -> list[Article]:
        return [self.article] if self.article else []


class TicketUpdate(TicketBase):
    article: Article | None = None

    def get_articles(self) -> list[Article]:
        return [self.article] if self.article else []


class Ticket(TicketBase):
    id: int
    articles: list[Article] = []

    def get_articles(self) -> list[Article]:
        return self.articles or []


class TicketSearch(BaseModel):
    limit: int = 50
    changed_newer_than_datetime: datetime | None = None
    changed_older_than_datetime: datetime | None = None
