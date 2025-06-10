import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from api.initialize.redis import RedisInitializer
import logging
import uuid
import os
from pydantic import BaseModel

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

class TokenResponse(BaseModel):
    token: str
    expires_at: datetime
    token_type: str

async def check_blacklist(token: str) -> bool:
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

def create_token(uuid_token: str) -> str:
    # 1. Set time expiration
    time_ex = os.getenv("ACCESS_TOKEN", "72h")

    # Parse duration string like "72h" into timedelta
    try:
        if time_ex.endswith("h"):
            hours = int(time_ex[:-1])
            expiration = timedelta(hours=hours)
        else:
            raise ValueError("Invalid time format")
    except Exception as e:
        raise e

    now = datetime.utcnow()
    expires_at = now + expiration

    payload = {
        "jti": str(uuid.uuid4()),
        "exp": int(expires_at.timestamp()),
        "iat": int(now.timestamp()),
        "iss": "parkingdevgo",
        "sub": uuid_token
    }

    # Replace with your actual secret key
    secret_key = os.getenv("SECRET_KEY", "Thaco@1234")

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    
    return TokenResponse(
        token=token,
        expires_at=expires_at,
        token_type="Bearer"
    )

def create_refresh_token(uuid_token: str) -> str:
    # 1. Set time expiration
    time_ex = os.getenv("REFRESH_TOKEN", "168h")

    # Parse duration string like "168h" into timedelta
    try:
        if time_ex.endswith("h"):
            hours = int(time_ex[:-1])
            expiration = timedelta(hours=hours)
        else:
            raise ValueError("Invalid time format")
    except Exception as e:
        raise e

    now = datetime.utcnow()
    expires_at = now + expiration

    payload = {
        "jti": str(uuid.uuid4()),
        "exp": int(expires_at.timestamp()),
        "iat": int(now.timestamp()),
        "iss": "parkingdevgo",
        "sub": uuid_token
    }

    # Replace with your actual secret key
    secret_key = os.getenv("SECRET_KEY", "Thaco@1234")

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token