from typing import Optional
import redis
import asyncpg
from minio import Minio
from casbin import Enforcer

class global_instance:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(global_instance, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config = None
        self.logger = None
        self.pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.minio_client: Optional[Minio] = None
        self.enforcer: Optional[Enforcer] = None

# Create a global instance
global_instance = global_instance() 