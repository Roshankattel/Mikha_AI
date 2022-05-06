
# Set up our OIDC
from typing import Callable
from fastapi_oidc import IDToken
from fastapi_oidc import get_auth
from config import settings

OIDC_config = {
    "client_id": f"{settings.client_id}",
    "base_authorization_server_uri": f"{settings.base_authorization_server_uri}",
    "audience": f"{settings.audience}",
    "issuer": f"{settings.issuer}",
    "signature_cache_ttl": settings.signature_cache_ttl,
}

authenticate_user: Callable = get_auth(**OIDC_config)
