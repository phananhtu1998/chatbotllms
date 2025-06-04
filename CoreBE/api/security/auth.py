from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

# Define security schemes
security = HTTPBearer()
api_key_security = APIKeyHeader(name="X-API-Key")

async def get_bearer_token(bearer_token: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency for Bearer token authentication"""
    if bearer_token:
        # In a real application, you would validate the token here
        return bearer_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_api_key(api_key: str = Depends(api_key_security)):
    """Dependency for API Key authentication"""
    if api_key:
        # In a real application, you would validate the API key here
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "X-API-Key"},
    )

async def get_api_key_or_bearer(bearer_token: HTTPAuthorizationCredentials = Depends(security), api_key: str = Depends(api_key_security)):
    """Dependency to allow authentication with either API Key or Bearer Token"""
    if bearer_token or api_key:
        # In a real application, you would validate the token/key here
        return bearer_token or api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer or X-API-Key"},
    ) 