import os
import sys
import logging
from pathlib import Path
from api.initialize.run import ApplicationRunner

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Configure logging for the application"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = os.getenv('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add file handler if LOG_TO_FILE is enabled
    if os.getenv('LOG_TO_FILE', 'false').lower() == 'true':
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    
    # Set specific log levels for third-party libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.INFO)


def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = project_root / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logging.info(f"Loaded environment variables from {env_file}")
        except ImportError:
            logging.warning("python-dotenv not installed, skipping .env file loading")


def validate_environment():
    """Validate required environment variables"""
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL', 
        'OPENSEARCH_URL',
        'MINIO_ENDPOINT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logging.info("Application will attempt to start with default values")


def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        load_environment()
        validate_environment()
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        reload = True  # Always enable reload mode to have SwaggerUI
        logger.info("=" * 60)
        logger.info("Starting ChatBot Local LLM API")
        logger.info("=" * 60)
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
        logger.info(f"Reload mode: {reload}")
        logger.info(f"Docs URL: http://{host}:{port}/docs")
        logger.info("=" * 60)
        runner = ApplicationRunner()
        runner.run(host=host, port=port, reload=reload)
    except KeyboardInterrupt:
        logger.info("\nApplication stopped by user (Ctrl+C)")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        logger.exception("Full error traceback:")
        sys.exit(1)


def create_app():
    """Create FastAPI app instance for ASGI servers like gunicorn"""
    setup_logging()
    load_environment()
    
    runner = ApplicationRunner()
    return runner.create_app()

app = create_app()

if __name__ == "__main__":
    main()