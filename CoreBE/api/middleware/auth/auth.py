from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import logging
import sys
from api.utils.auth.jwt import verify_token_subject,check_blacklist,check_token_revoked

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Get logger for this module
logger = logging.getLogger(__name__)

class AuthMiddleware:
    def __init__(self):
        self.security = HTTPBearer()
        self.api_key_security = APIKeyHeader(name="X-API-Key")

    async def get_bearer_token(self, request: Request, bearer_token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Dependency for Bearer token authentication"""
        if bearer_token:
            # get token auth
            tokenauth = bearer_token.credentials
            # verify token
            token_claims, error = await verify_token_subject(tokenauth)
            if error:
                logger.error(f"Error verifying token: {error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            # check blacklist
            isblacklisted = await check_blacklist(token_claims.sub)
            if isblacklisted:
                logger.error("Token is blacklisted")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is blacklisted",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            # check token revoked by change password
            isrevoked, error = await check_token_revoked(token_claims.sub, token_claims.iat)
            if error:
                logger.error(f"Error checking token revoked: {error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if isrevoked:
                logger.error("Token is revoked")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"}
                )  
            # Add subject UUID to request state
            logger.info(f"claims::: UUID:: {token_claims.sub}")
            request.state.subject_uuid = token_claims.sub
            return bearer_token
            
        logger.warning("No bearer token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def get_api_key(self, api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
        """Dependency for API Key authentication"""
        if api_key:
            # In a real application, you would validate the API key here
            return api_key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "X-API-Key"},
        )

    async def get_api_key_or_bearer(self, bearer_token: HTTPAuthorizationCredentials = Depends(HTTPBearer()), api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
        """Dependency to allow authentication with either API Key or Bearer Token"""
        if bearer_token or api_key:
            logger.info("=== Auth Middleware Debug Info ===")
            if bearer_token:
                logger.info(f"Bearer Token Credentials: {bearer_token.credentials}")
            if api_key:
                logger.info(f"API Key: {api_key}")
            return bearer_token or api_key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer or X-API-Key"},
        )

# Create a singleton instance
auth_middleware = AuthMiddleware() 