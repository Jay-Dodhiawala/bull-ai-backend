from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

load_dotenv()

class SupabaseClientManager:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._client:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client with error handling"""
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            
            if not url or not key:
                raise ValueError("Missing Supabase credentials in environment variables")
            
            self._client = create_client(url, key)
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    @property
    def client(self):
        """Get the Supabase client instance"""
        return self._client

@lru_cache(maxsize=1)
def create_supabase_client():
    """Create or get cached Supabase client"""
    return SupabaseClientManager().client

# Singleton instance for backward compatibility
supabase_client = create_supabase_client()