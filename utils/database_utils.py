from qdrant_client.client_base import QdrantBase
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client
from dotenv import load_dotenv
import os

from typing import List
from langchain_core.documents import Document

from utils.my_tools import hash_document

load_dotenv()



def create_db_client():
    try:
        print("Connecting to Supabase...")
        supabase_client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        return supabase_client
    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")



def create_vector_store(client: Client):  # kept collection_name parameter for compatibility
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=os.getenv("OPENAI_API_KEY")
    )

    return SupabaseVectorStore(

        embedding=embeddings,
        client=client,
        table_name="chunks_v2",
        query_name="match_chunks_v2"
    )

