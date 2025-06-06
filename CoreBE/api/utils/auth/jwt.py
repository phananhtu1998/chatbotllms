import jwt
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from api.initialize.redis import RedisInitializer
import logging

logger = logging.getLogger(__name__)

# Initialize Redis
redis_init = RedisInitializer()

class TokenClaims:
    def __init__(self, claims: Dict[str, Any]):
        self.exp = claims.get('exp')
        self.iat = claims.get('iat')
        self.nbf = claims.get('nbf')
        self.sub = claims.get('sub')
        self.iss = claims.get('iss')
        self.aud = claims.get('aud')

async def check_blacklist(token: str) -> bool:
    """
    Check if token is in blacklist
    
    Args:
        token (str): Token to check
        
    Returns:
        bool: True if token is blacklisted, False otherwise
    """
    try:
        if not redis_init.client:
            await redis_init.initialize()
            
        # Create Redis key in correct format
        redis_key = f"TOKEN_BLACK_LIST_{token}"
        
        # Check if key exists in Redis
        result = await redis_init.client.get(redis_key)
        
        # If result exists, token is blacklisted
        if result is not None:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error checking Redis blacklist: {e}")
        return False

async def verify_token_subject(token: str) -> Tuple[Optional[TokenClaims], Optional[Exception]]:
    """
    Verify JWT token and return claims if valid
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        Tuple[Optional[TokenClaims], Optional[Exception]]: Tuple containing claims and error if any
    """
    try:
        # Check blacklist first
        if await check_blacklist(token):
            return None, Exception("token is blacklisted")
            
        # Parse the token
        claims = jwt.decode(token, options={"verify_signature": False})
        
        # Convert to TokenClaims object
        token_claims = TokenClaims(claims)
        
        # Validate claims
        if token_claims.exp and datetime.utcnow().timestamp() > token_claims.exp:
            return None, Exception("token has expired")
            
        if token_claims.nbf and datetime.utcnow().timestamp() < token_claims.nbf:
            return None, Exception("token is not valid yet")
            
        return token_claims, None
        
    except jwt.InvalidTokenError as e:
        return None, e
    except Exception as e:
        return None, e

async def check_token_revoked(subtoken: str, issued_at: int) -> Tuple[bool, Optional[Exception]]:
    """
    Check if token is revoked due to password change
    
    Args:
        subtoken (str): Subtoken to check
        issued_at (int): Token issued timestamp
        
    Returns:
        Tuple[bool, Optional[Exception]]: Tuple containing revocation status and error if any
    """
    try:
        if not redis_init.client:
            await redis_init.initialize()
            
        # Get user info from cache
        user_info_key = f"USER_INFO_{subtoken}"
        user_info = await redis_init.client.get(user_info_key)
        
        if not user_info:
            logger.info("No user info found in cache, assuming token not revoked")
            return False, None
            
        # Create Redis key for password change timestamp
        invalidation_key = f"TOKEN_IAT_AVAILABLE_{user_info.decode()}"
        
        # Get password change timestamp from Redis
        change_password_timestamp = await redis_init.client.get(invalidation_key)
        
        if not change_password_timestamp:
            logger.info("No password change timestamp found, token not revoked")
            return False, None
            
        # Convert timestamp to int
        try:
            change_password_timestamp = int(change_password_timestamp.decode())
        except ValueError as e:
            logger.error(f"Error parsing timestamp from Redis: {e}")
            return False, Exception(f"Error parsing timestamp from Redis: {e}")
            
        # Check if token is revoked due to password change
        if issued_at < change_password_timestamp:
            logger.info("Token revoked due to password change")
            return True, None
            
        return False, None
        
    except Exception as e:
        logger.error(f"Error checking token revocation: {e}")
        return False, e
