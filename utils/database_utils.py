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


# class SupabaseVectorStore:
#     def __init__(self, client: Client, embedding_model: OpenAIEmbeddings, table_name: str = "chunks_v2"):
#         self.client = client
#         self.embedding_model = embedding_model
#         self.table_name = table_name

#     def as_retriever(self, **kwargs):
#         return self
    
#     def invoke(self, query: str, top_k: int = 4) -> List[Document]:
#         # Generate embedding for the query
#         query_embedding = self.embedding_model.embed_query(query)
        
#         # Perform similarity search using Supabase's match_documents function
#         response = (
#             self.client.rpc(
#                 'match_documents_from_chunks_v2',
#                 {
#                     'query_embedding': query_embedding,
#                     'match_count': top_k
#                 }
#             ).execute()
#         )
        
#         # Convert results to Documents
#         documents = []
#         for item in response.data:
#             doc = Document(
#                 page_content=item['content'],
#                 metadata=item.get('metadata', {})
#             )
#             documents.append(doc)
            
#         return documents




def create_db_client():
    try:
        # qdrant_client = QdrantClient(
        #     os.getenv("QDRANT_HOST"),
        #     api_key=os.getenv("QDRANT_API_KEY"),
        # )

        # return qdrant_client
        print("Connecting to Supabase...")
        supabase_client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        return supabase_client
    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")


# def create_collection_if_not_exists(client:QdrantBase, collection_name:str):
#     try:
#         collection_info = client.get_collection(collection_name)
#         print(f"Collection '{collection_name}' already exists.")
#         # return collection_info
#     except Exception as e:
#         print(f"Collection '{collection_name}' does not exist. Creating it now.")
#         vectors_config = models.VectorParams(
#             size=1536, 
#             distance=models.Distance.COSINE
#         )
#         client.create_collection(
#             collection_name=collection_name,
#             vectors_config=vectors_config,
#         )
#         print(f"Collection '{collection_name}' created successfully.")
        # return client.get_collection(collection_name)
    
    
# def create_vector_store(client:QdrantBase, collection_name:str):



#     # load_dotenv()
#     create_collection_if_not_exists(client, collection_name)
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

#     vectorstore = QdrantVectorStore(
#         client = client,
#         embedding=embeddings, 
#         collection_name=collection_name
#     )

#     return vectorstore

def create_vector_store(client: Client):  # kept collection_name parameter for compatibility
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=os.getenv("OPENAI_API_KEY")
    )

    return SupabaseVectorStore(
        # client=client,
        # embedding_model=embeddings,
        # table_name="chunks_v2"  # hardcoded since we're only reading from this table

        embedding=embeddings,
        client=client,
        table_name="chunks_v2",
        query_name="match_chunks_v2"
    )


# def add_documents(client:QdrantBase, collection_name:str, vectorstore:QdrantVectorStore, chunks:List[Document], company_name:str):
#     for doc in chunks:
#         doc_hash = hash_document(doc.page_content)
        
#         # Check if the document already exists
#         search_result = client.scroll(
#             collection_name=collection_name,
#             scroll_filter=models.Filter(
#                 must=[
#                     models.FieldCondition(
#                         key="metadata.doc_hash",
#                         match=models.MatchValue(value=doc_hash)
#                     ),
#                     models.FieldCondition(
#                         key="metadata.company",
#                         match=models.MatchValue(value=company_name)
#                     )
#                 ]
#             ),
#             limit=1
#         )
        
#         if not search_result[0]:  # Document doesn't exist
#             vectorstore.add_texts(
#                 texts=[doc.page_content],
#                 metadatas=[{"doc_hash": doc_hash, "company": company_name,**doc.metadata}]
#             )
#             print(f"Added document with hash: {doc_hash}")
#         else:
#             print(f"Document with hash {doc_hash} already exists. Skipping.")




