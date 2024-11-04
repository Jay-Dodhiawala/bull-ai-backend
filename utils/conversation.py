from langchain_community.chat_models import ChatPerplexity
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from typing import Any
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatPerplexity(
    temperature=0, 
    pplx_api_key=os.getenv("PPXL_API_KEY"), 
    model="llama-3.1-sonar-small-128k-online"
)

def get_conversation_chain(vectorstore: SupabaseVectorStore, company_name: str = None):
    if company_name:
        # Company-specific prompt
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't find the answer in the context, use your general knowledge to provide a response be concise.
        NOTE - This is for Indian stock markets only so use the currency properly number system is in lakhs and crores. And let me know if you used context or general knowledge to answer the question.
        CHARACTER LIMIT - 1000 characters only.

        Context: {context}

        Question: {question}

        Answer: """
    else:
        # General market prompt
        prompt_template = """Use the following pieces of context to answer the question about the Indian stock market. If you don't find the answer in the context, use your general knowledge about Indian markets to provide a response.
        NOTE - This is for Indian stock markets only so use the currency properly number system is in lakhs and crores. And let me know if you used context or general knowledge to answer the question.
        CHARACTER LIMIT - 1000 characters only.

        Context: {context}

        Question: {question}

        Answer: """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    retriever = vectorstore.as_retriever()

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
    return conversation_chain

def handle_conversation(conversation: Any, user_question: str, company_name: str = None):
    if company_name:
        # For company-specific questions
        if company_name.lower() not in user_question.lower():
            user_question = f"Regarding {company_name}, {user_question}"
    else:
        # For general market questions
        if not any(term in user_question.lower() for term in ['market', 'nifty', 'sensex', 'india', 'indian']):
            user_question = f"Regarding the Indian stock market, {user_question}"
        
    response = conversation.invoke({'question': user_question})
    return response['answer']