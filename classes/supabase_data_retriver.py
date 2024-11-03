from utils.supabase_client import supabase_client
import logging
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger(__name__)

class SecurityDataRetriever:
    def __init__(self):
        self.supabase = supabase_client
        self._security_codes_cache = {}
        self._document_ids_cache = {}

    @lru_cache(maxsize=1000)
    def get_security_code(self, company_name: str) -> Optional[str]:
        """Get security code with caching"""
        try:
            response = self.supabase.table('securities')\
                .select('security_code')\
                .eq('security_id', company_name.upper())\
                .execute()
            
            return response.data[0]['security_code'] if response.data else None
            
        except Exception as e:
            logger.error(f"Error fetching security code for {company_name}: {e}")
            return None

    @lru_cache(maxsize=1000)
    def get_document_ids(self, security_code: str) -> List[str]:
        """Get document IDs with caching"""
        try:
            response = self.supabase.table('documents')\
                .select('id')\
                .eq('company_code', security_code)\
                .execute()
            
            return [doc['id'] for doc in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching document IDs for {security_code}: {e}")
            return []
        
    @lru_cache(maxsize=1000)
    def get_document_ids_from_name(self, security_name: str) -> List[str]:
        """Get document IDs with caching"""
        try:
            security_code = self.get_security_code(security_name)
            return self.get_document_ids(security_code)
            
        except Exception as e:
            logger.error(f"Error fetching document IDs for {security_code}: {e}")
            return []
        
    @lru_cache(maxsize=1000)
    def get_document(self, doc_id: str) -> Optional[dict]:
        """Get document details by ID"""
        try:
            response = self.supabase.table('documents')\
                .select('*')\
                .eq('id', doc_id)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error fetching document {doc_id}: {e}")
            return None

    def get_all_securities_codes(self) -> List[str]:
        """Get all security codes with batching"""
        try:
            codes = []
            batch_size = 1000
            total_count = 3000

            for start in range(0, total_count, batch_size):
                end = start + batch_size - 1
                response = self.supabase.table('securities')\
                    .select('security_code')\
                    .range(start, end)\
                    .execute()
                
                codes.extend(sec['security_code'] for sec in response.data)
            
            return codes
            
        except Exception as e:
            logger.error(f"Error fetching all security codes: {e}")
            return []

    def refresh_caches(self):
        """Clear all caches"""
        self.get_security_code.cache_clear()
        self.get_document_ids.cache_clear()
        self._security_codes_cache.clear()
        self._document_ids_cache.clear()

# Singleton instance
security_retriever = SecurityDataRetriever()