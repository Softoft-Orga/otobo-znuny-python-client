from typing import Dict

from pydantic import BaseModel, Field

from otobo.domain_models.basic_auth_model import BasicAuth
from otobo.domain_models.ticket_operation import TicketOperation

type OperationUrlMap = dict[TicketOperation, str]

class ClientConfig(BaseModel):
    base_url: str
    webservice_name: str
    operation_url_map: OperationUrlMap


