from minio import Minio
from minio.error import S3Error
import logging
import os

logger = logging.getLogger(__name__)

class MinIOInitializer:
    def __init__(self):
        self.client = None
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME', 'chatbot-files')
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
    
    def initialize(self):
        """Initialize MinIO client and create buckets"""
        try:
            # Create MinIO client
            self.client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # Test connection
            self._test_connection()
            
            # Create buckets
            self._create_buckets()
            
            logger.info("MinIO storage initialized successfully")
            return self.client
            
        except Exception as e:
            logger.error(f"Error initializing MinIO: {str(e)}")
            raise
    
    def _test_connection(self):
        """Test MinIO connection"""
        try:
            # List buckets to test connection
            buckets = self.client.list_buckets()
            logger.info(f"MinIO connection successful. Found {len(buckets)} buckets")
            
        except S3Error as e:
            logger.error(f"MinIO connection failed: {str(e)}")
            raise
    
    def _create_buckets(self):
        """Create required buckets"""
        buckets_to_create = [
            self.bucket_name,
            f"{self.bucket_name}-models",
            f"{self.bucket_name}-documents",
            f"{self.bucket_name}-temp"
        ]
        
        for bucket in buckets_to_create:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
                else:
                    logger.info(f"Bucket already exists: {bucket}")
                    
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket}: {str(e)}")
                raise
    
    def set_bucket_policy(self, bucket_name: str, policy: dict):
        """Set bucket policy"""
        try:
            import json
            self.client.set_bucket_policy(bucket_name, json.dumps(policy))
            logger.info(f"Set policy for bucket: {bucket_name}")
            
        except S3Error as e:
            logger.error(f"Error setting bucket policy: {str(e)}")
            raise