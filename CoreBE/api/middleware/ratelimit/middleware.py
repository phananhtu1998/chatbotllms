from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
import logging
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Current time
        now = time.time()
        
        # Clean old requests
        while (self.clients[client_ip] and 
               now - self.clients[client_ip][0] > self.period):
            self.clients[client_ip].popleft()
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"message": "Rate limit exceeded. Too many requests."}
            )
        
        # Add current request
        self.clients[client_ip].append(now)
        
        return await call_next(request) 