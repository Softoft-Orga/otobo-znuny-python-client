
from pydantic import BaseModel

from otobo_znuny.domain_models.ticket_operation import TicketOperation

type OperationUrlMap = dict[TicketOperation, str]

class ClientConfig(BaseModel):
    base_url: str
    webservice_name: str
    operation_url_map: OperationUrlMap


