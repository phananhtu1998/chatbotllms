import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger("api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Log request start
        logger.info(f"Started {method} {path} from {client_host}")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response details
            logger.info(
                f"Completed {response.status_code} in {process_time:.3f}s - {method} {path}"
            )
            
            return response
            
        except Exception as e:
            # Log any errors
            process_time = time.time() - start_time
            logger.error(
                f"Error processing {method} {path} - {str(e)} - {process_time:.3f}s"
            )
            raise

def setup_logging(app):
    """Setup logging middleware for the application"""
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("Logging middleware initialized")

def log_request(request: Request, response: Response, process_time: float):
    """Log detailed request information"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time": f"{process_time:.3f}s",
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    
    logger.info(json.dumps(log_data))
