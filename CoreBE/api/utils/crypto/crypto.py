import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get SECRET_KEY from environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
class Crypto:
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        # Combine password, salt and secret key
        salted_password = f"{password}{salt}{SECRET_KEY}"
        # Create SHA256 hash
        hash_obj = hashlib.sha256(salted_password.encode('utf-8'))
        return hash_obj.hexdigest()

    @staticmethod
    def matching_password(store_hash: str, password: str, salt: str) -> bool:
        hash_password_result = Crypto.hash_password(password, salt)
        return store_hash == hash_password_result
