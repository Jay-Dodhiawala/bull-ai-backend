from qdrant_client.client_base import QdrantBase
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

from typing import List
from langchain_core.documents import Document

from utils.my_tools import hash_document

load_dotenv()

def create_db_client():
    try:
        qdrant_client = QdrantClient(
            os.getenv("QDRANT_HOST"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )

        return qdrant_client
    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")


def create_collection_if_not_exists(client:QdrantBase, collection_name:str):
    try:
        collection_info = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' already exists.")
        # return collection_info
    except Exception as e:
        print(f"Collection '{collection_name}' does not exist. Creating it now.")
        vectors_config = models.VectorParams(
            size=1536, 
            distance=models.Distance.COSINE
        )
        client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
        )
        print(f"Collection '{collection_name}' created successfully.")
        # return client.get_collection(collection_name)
    
    
def create_vector_store(client:QdrantBase, collection_name:str):
    # load_dotenv()
    create_collection_if_not_exists(client, collection_name)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

    vectorstore = QdrantVectorStore(
        client = client,
        embedding=embeddings, 
        collection_name=collection_name
    )

    return vectorstore

def add_documents(client:QdrantBase, collection_name:str, vectorstore:QdrantVectorStore, chunks:List[Document], company_name:str):
    for doc in chunks:
        doc_hash = hash_document(doc.page_content)
        
        # Check if the document already exists
        search_result = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.doc_hash",
                        match=models.MatchValue(value=doc_hash)
                    ),
                    models.FieldCondition(
                        key="metadata.company",
                        match=models.MatchValue(value=company_name)
                    )
                ]
            ),
            limit=1
        )
        
        if not search_result[0]:  # Document doesn't exist
            vectorstore.add_texts(
                texts=[doc.page_content],
                metadatas=[{"doc_hash": doc_hash, "company": company_name,**doc.metadata}]
            )
            print(f"Added document with hash: {doc_hash}")
        else:
            print(f"Document with hash {doc_hash} already exists. Skipping.")




