from langchain_community.chat_models import ChatPerplexity
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from typing import Any
from langchain_qdrant import QdrantVectorStore

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from dotenv import load_dotenv
import os

load_dotenv()

# print(os.getenv("PPXL_API_KEY"))

llm = ChatPerplexity(
    temperature=0, 
    pplx_api_key=os.getenv("PPXL_API_KEY"), 
    model="llama-3.1-sonar-small-128k-online"
)

def get_conversation_chain(vectorstore:QdrantVectorStore, company_name:str):

    retirever = vectorstore.as_retriever(
        kwargs={"filter": lambda doc: doc.metadata.get("company") == company_name}
    )

    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't find the answer in the context, use your general knowledge to provide a response be concise.
    NOTE - This is for Indian stock markets only so use the currency properly number system is in lakhs and crores. And let me know if oyu used context or general knowledge to answer the question.
    CHARACTER LIMIT - 1000 characters only.

    Context: {context}

    Question: {question}

    Answer: """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retirever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
    return conversation_chain

def handle_conversation(conversation:Any, user_question:str, company_name:str):
    # Inject the company name into the question if not already present
    if company_name.lower() not in user_question.lower():
        user_question = f"Regarding {company_name}, {user_question}"
        
    response = conversation.invoke({'question': user_question})
    return response['answer']
