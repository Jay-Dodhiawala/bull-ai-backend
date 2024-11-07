from langchain_community.chat_models import ChatPerplexity
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

from typing import Any
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from dotenv import load_dotenv
import os

from prompts import PROMPT_TEMPLATES
from classes.supabase_data_retriver import SecurityDataRetriever

load_dotenv()

llm = ChatPerplexity(
    temperature=0, 
    pplx_api_key=os.getenv("PPXL_API_KEY"), 
    model="llama-3.1-sonar-small-128k-online"
)

security_retriever = SecurityDataRetriever()

def get_conversation_chain(vectorstore: SupabaseVectorStore, company_name: str = None):
    # Initialize memory first
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    if company_name:
        # Company-specific prompt
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't find the answer in the context, use your general knowledge to provide a response be concise.
        NOTE - This is for Indian stock markets only so use the currency properly number system is in lakhs and crores. And let me know if you used context or general knowledge to answer the question.
        CHARACTER LIMIT - 1000 characters only.

        Context: {context}

        Question: {question}

        Answer: """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        
        # Use retriever only for company-specific questions
        retriever = vectorstore.as_retriever()
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt}
        )
    else:
        # For general market questions, use a simple chain without retriever
        prompt_template = PROMPT_TEMPLATES["general_market"]
        prompt = PromptTemplate(template=prompt_template, input_variables=["question"])
        
        # Use a simple chain for general market questions
        conversation_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=memory
        )
    
    return conversation_chain

def handle_conversation(conversation: Any, user_question: str, company_name: str = None):
    if company_name:
        # Check if the question is about comparing companies
        is_comparison_question = any(keyword in user_question.lower() for keyword in ["compare", "other", "different", "top", "best"])

        if company_name.lower() not in user_question.lower() and not is_comparison_question:
            user_question = f"Regarding {company_name}, {user_question}"

        retriever_output = conversation.retriever.invoke(user_question)[:3]
        
        if not retriever_output:
            return f"I'm sorry, but I don't have any specific information about {company_name} in my database. Could you please ask a more general question?"
        
        doc_list = security_retriever.get_document_ids_from_name(company_name)
        context = ""
        for doc in retriever_output:
            doc_id = doc.metadata["document_id"]
            if doc_id in doc_list:
                category = security_retriever.get_document(doc_id)["category_name"]
                context += f"# {category} of {company_name}\n\n{doc.page_content}\n\n\n\n"
            else:
                continue
        
        combined_input = f"Context: {context}\n\nQuestion: {user_question}"
        response = conversation.invoke({'question': combined_input})
        return response['answer']
    else:
        # For general market questions
        if not any(term in user_question.lower() for term in ['market', 'nifty', 'sensex', 'india', 'indian']):
            user_question = f"Regarding the Indian stock market, {user_question}"
        
        response = conversation.invoke({'question': user_question})
        return response['text']