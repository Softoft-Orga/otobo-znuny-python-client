"""Public package interface for the OTOBO client library.

Historically the project relied on implicit absolute imports which only
worked once the package had been installed.  The test-suite imports the
package directly from the repository, so we expose the key classes and
utilities here using explicit relative imports.  This keeps the package
importable without installation and avoids circular import issues.
"""

from .models.client_config_models import *  # noqa: F401,F403
from .models.request_models import (
    TicketGetRequest,
    TicketSearchRequest,
    TicketUpdateRequest,
    AuthData,
)
from .models.response_models import *  # noqa: F401,F403
from .client.otobo_client import OTOBOClient
from .util.otobo_errors import OTOBOError
from .util.webservice_config import create_otobo_client_config

# Backwards compatibility alias; some documentation refers to this name.
from .models.response_models import TicketResponse as OTOBOTicketCreateResponse

__all__ = [
    "AuthData",
    "TicketOperation",
    "OTOBOTicketCreateResponse",
    "TicketUpdateResponse",
    "TicketSearchResponse",
    "TicketGetResponse",
    "TicketGetRequest",
    "TicketUpdateRequest",
    "TicketSearchRequest",
    "OTOBOClientConfig",
    "OTOBOError",
    "OTOBOClient",
    "create_otobo_client_config",
]
