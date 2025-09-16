# tests/factories.py
import time
import uuid
from dataclasses import dataclass
from otobo import TicketCreateRequest

DEFAULT_CONTENT_TYPE = "text/plain; charset=utf-8"

@dataclass
class TicketBase:
    title: str
    queue: str = "Raw"
    state: str = "new"
    priority: str = "3 normal"
    type: str = "Incident"
    customer_user: str = "customer@localhost.de"
    subject: str = "Integration Test"
    body: str = "pytest body"
    content_type: str = DEFAULT_CONTENT_TYPE

    def to_create_request(self) -> TicketCreateRequest:
        return TicketCreateRequest(
            Ticket=TicketCreateFields(
                Title=self.title,
                Queue=self.queue,
                State=self.state,
                Priority=self.priority,
                Type=self.type,
                CustomerUser=self.customer_user,
            ),
            Article=ArticleCreate(
                Subject=self.subject,
                Body=self.body,
                ContentType=self.content_type,
            ),
        )

def make_ticket_base(prefix: str = "pytest", **overrides) -> TicketBase:
    title = f"{prefix}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    return TicketBase(title=title, **overrides)

def make_ticket_bases(count: int, prefix: str = "pytest", **overrides) -> list[TicketBase]:
    return [make_ticket_base(prefix=prefix, **overrides) for _ in range(count)]

def make_create_requests(bases: list[TicketBase]) -> list[TicketCreateRequest]:
    return [b.to_create_request() for b in bases]
