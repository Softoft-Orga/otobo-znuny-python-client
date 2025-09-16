# tests/datasets.py
import asyncio
from typing import Dict, List
from tests.factories import make_ticket_base, make_create_requests
from otobo import TicketCreateRequest

def build_dataset_spec(count_per_queue: Dict[str, int], prefix: str = "seed", **overrides) -> list:
    bases = []
    for queue, n in count_per_queue.items():
        for _ in range(n):
            bases.append(make_ticket_base(prefix=prefix, queue=queue, **overrides))
    return bases

def build_requests_for_spec(bases: list) -> list[TicketCreateRequest]:
    return make_create_requests(bases)

async def create_dataset(otobo_client, count_per_queue: Dict[str, int], prefix: str = "seed", **overrides) -> Dict[str, List[int]]:
    bases = build_dataset_spec(count_per_queue, prefix=prefix, **overrides)
    reqs = build_requests_for_spec(bases)
    ids = await asyncio.gather(*[otobo_client.create_ticket(r) for r in reqs])
    by_queue: Dict[str, List[int]] = {}
    i = 0
    for queue, n in count_per_queue.items():
        chunk = [int(x.TicketID) for x in ids[i:i+n]]
        by_queue.setdefault(queue, []).extend(chunk)
        i += n
    return by_queue
