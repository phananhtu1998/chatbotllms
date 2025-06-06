from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import logging
import sys

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Get logger for this module
logger = logging.getLogger(__name__)

# Define security schemes
security = HTTPBearer()
api_key_security = APIKeyHeader(name="X-API-Key")

async def get_bearer_token(request: Request, bearer_token: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency for Bearer token authentication"""
    # Log request headers
    logger.info("=== Auth Middleware Debug Info ===")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    if bearer_token:
        logger.info(f"Bearer Token received - Scheme: {bearer_token.scheme}")
        logger.info(f"Bearer Token received - Credentials: {bearer_token.credentials}")
        return bearer_token
        
    logger.warning("No bearer token provided")
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
        logger.info("=== Auth Middleware Debug Info ===")
        logger.info(f"Bearer Token: {bearer_token}")
        logger.info(f"API Key: {api_key}")
        # In a real application, you would validate the token/key here
        return bearer_token or api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer or X-API-Key"},
    ) 