import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import os
from .logging import setup_logging, RequestLoggingMiddleware
from colorama import Fore, Style, init

init(autoreset=True)

from .redis import RedisInitializer
from .router import RouterInitializer
from api.middleware.ratelimit.middleware import RateLimitMiddleware

# Define security schemes
security = HTTPBearer()
api_key_security = APIKeyHeader(name="X-API-Key")

async def get_api_key_or_bearer(bearer_token: HTTPAuthorizationCredentials = Depends(security), api_key: str = Depends(api_key_security)):
    """Dependency to allow authentication with either API Key or Bearer Token"""
    if bearer_token or api_key:
        # In a real application, you would validate the token/key here
        # For now, we just check if either is present
        return bearer_token or api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer or X-API-Key"},
    )

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    def format(self, record):
        if record.levelno == logging.INFO:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

# Configure logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)

logger = logging.getLogger(__name__)

class ApplicationRunner:
    def __init__(self):
        self.app = None
        self.redis_client = None
        self.minio_client = None
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Application lifespan manager"""
        # Startup
        logger.info("Starting application...")
        
        try:
            await self._initialize_services()
            logger.info("Application started successfully")
            yield
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}")
            raise
        finally:
            # Shutdown
            logger.info("Shutting down application...")
            await self._cleanup_services()
            logger.info("Application shutdown completed")
    
    async def _initialize_services(self):
        """Initialize all services"""
        # Initialize Redis
        redis_init = RedisInitializer()
        self.redis_client = await redis_init.initialize()
    async def _cleanup_services(self):
        """Cleanup all services"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def create_app(self):
        """Create FastAPI application"""
        
        # Create FastAPI app with lifespan
        self.app = FastAPI(
            title="ChatBot Local LLM API",
            description="Advanced chatbot API using local LLM models",
            version="1.0.0",
            lifespan=self.lifespan,
            docs_url="/docs",  # Always enable SwaggerUI
            redoc_url="/redoc"  # Always enable ReDoc
        )
        self.app.swagger_ui_parameters = {
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "tryItOutEnabled": True
        }
        
        # Add rate limit middleware
        self.app.add_middleware(
            RateLimitMiddleware,
            calls=3,  # Số request tối đa trong một khoảng thời gian
            period=60   # Khoảng thời gian tính bằng giây (60 giây = 1 phút)
        )
        
        # Add request logging middleware
        self.app.add_middleware(RequestLoggingMiddleware)
        
        # Initialize routers
        router_init = RouterInitializer()
        main_router = router_init.initialize()
        
        # Include main router
        self.app.include_router(main_router, prefix="/api/v1", dependencies=[Depends(get_api_key_or_bearer)])
        
        # Add health check endpoint
        @self.app.get("/health")
        async def health_check():
            logger.info("Health check endpoint called")
            return {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "postgres": "connected" if self.postgres_pool else "disconnected",
                    "redis": "connected" if self.redis_client else "disconnected",
                    "opensearch": "connected" if self.opensearch_client else "disconnected",
                    "minio": "connected" if self.minio_client else "disconnected"
                }
            }
        
        return self.app
    
    def run(self, host="0.0.0.0", port=8000, reload=False):
        """Run the application"""
        if reload:
            # When using reload, we need to use the module path
            uvicorn.run(
                "api.main:app",
                host=host,
                port=port,
                reload=reload,
                log_level="info"
            )
        else:
            # When not using reload, we can use the app instance
            app = self.create_app()
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=reload,
                log_level="info"
            )