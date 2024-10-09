from utils.conversation import get_conversation_chain, handle_conversation

def generate_response(user_question, company_name, vectorstore):
    conversation = get_conversation_chain(vectorstore, company_name)
    response = handle_conversation(conversation, user_question, company_name)
    return response
    