from langchain_community.chat_models import ChatPerplexity
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from typing import Any
from langchain_qdrant import QdrantVectorStore

from collections import defaultdict
from classes.supabase_data_retriver import security_retriever

from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatPerplexity(
    temperature=0, 
    pplx_api_key=os.getenv("PPXL_API_KEY"), 
    model="llama-3.1-sonar-small-128k-online"
)

# def process_retrieved_documents(docs, company_name):
#     company_info = defaultdict(list)
#     for doc in docs:
#         doc_company = doc.metadata.get("company", "unknown")
#         # company_info[doc_company].append(f"[{doc_company}] {doc.page_content}")
#         print(doc_company)
#         company_info[doc_company].append(doc.page_content)
    
#     primary_company_info = company_info.get(company_name, [])
#     other_companies_info = {k: v for k, v in company_info.items() if k != company_name}

#     print(len(primary_company_info), len(other_companies_info))
    
#     return primary_company_info, other_companies_info
#     # return company_info

def get_conversation_chain(vectorstore, company_name:str):

    retirever = vectorstore.as_retriever(
        # search_kwargs={
        #     "filter": {
        #         "must": [
        #             {
        #                 "key": "company",
        #                 "match": {"value": company_name.upper()}
        #             }
        #         ]
        #     }
        # }
    )

    # prompt_template = """Use the following pieces of context to answer the question at the end. If you don't find the answer in the context, use your general knowledge to provide a response be concise.
    # NOTE - This is for Indian stock markets only so use the currency properly number system is in lakhs and crores. And let me know if oyu used context or general knowledge to answer the question.
    # CHARACTER LIMIT - 1000 characters only.

    # Context: {context}

    # Question: {question}

    # Answer: """

    prompt_template = """Use the following pieces of context to answer the question at the end. The context includes information about the primary company and may include information about other relevant companies. Use this information to answer the question as accurately as possible.

    If you don't find the complete answer in the context:
    1. Use whatever relevant information is available from the context.
    2. Clearly state which parts of your answer are based on the provided context and which parts are based on general knowledge.
    3. If using general knowledge, explicitly mention this in your answer.

    NOTE - This is for Indian stock markets only, so use the currency properly; number system is in lakhs and crores.
    CHARACTER LIMIT - 1000 characters only.

    {context}

    Question: {question}

    Answer: """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retirever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )


    return conversation_chain

# def handle_conversation(conversation: Any, user_question: str, company_name: str):
#     # Check if the question is about comparing companies
#     is_comparison_question = any(keyword in user_question.lower() for keyword in ["compare", "other", "different", "top", "best"])

#     if company_name.lower() not in user_question.lower() and not is_comparison_question:
#         user_question = f"Regarding {company_name}, {user_question}"

#     retriever_output = conversation.retriever.invoke(user_question)
    
#     if not retriever_output:
#         return f"I'm sorry, but I don't have any specific information about {company_name} in my database. Could you please ask a more general question?"
    
#     primary_info, other_info = process_retrieved_documents(retriever_output, company_name)

#     if(len(primary_info) == 0 and is_comparison_question == False):
#         return f"I'm sorry, but I don't have any specific information about {company_name} in my database. Could you please ask a more general question or inquire about a different company?"
    
#     context = f"Information about {company_name}: {' '.join(primary_info)}\n\n"
    
#     if is_comparison_question and other_info:
#         print("adding other company info")
#         context += "Information about other relevant companies:\n"
#         for company, info in other_info.items():
#             context += f"{company}: {' '.join(info)}\n"
    
#     # Combine context and question into a single input
#     combined_input = f"Context: {context}\n\nQuestion: {user_question}"
    
#     response = conversation.invoke({
#         'question': combined_input
#     })
    
#     return response['answer']

def handle_conversation(conversation, user_question: str, company_name: str):
    # Check if the question is about comparing companies
    is_comparison_question = any(keyword in user_question.lower() for keyword in ["compare", "other", "different", "top", "best"])

    if company_name.lower() not in user_question.lower() and not is_comparison_question:
        user_question = f"Regarding {company_name}, {user_question}"

    retriever_output = conversation.retriever.invoke(user_question)[:3]
    # print(user_question,company_name, len(retriever_output))
    print(retriever_output)
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
            # print(f"Document {doc_id} not found in database.")
            continue
    
    # Combine context and question into a single input
    combined_input = f"Context: {context}\n\nQuestion: {user_question}"
    
    response = conversation.invoke({
        'question': combined_input
    })
    
    return response['answer']
