from flask import Flask, request
from routes.GetResponse import generate_response
from utils.database_utils import create_db_client, create_vector_store, add_documents
import os
from twilio.twiml.messaging_response import MessagingResponse

user_states = {}

app = Flask(__name__)

@app.route('/')
def hello_world():
    bot_res = MessagingResponse()
    msg = bot_res.message()
    msg.body("hiiiiiiiiiii")
    return str(bot_res)

@app.route('/', methods=['POST'])
def handle_message():
    incoming_msg = request.form['Body'].strip().lower()
    sender = request.form['From']
    
    bot_res = MessagingResponse()
    msg = bot_res.message()

    if sender not in user_states:
        user_states[sender] = {'step': 'company_name'}
        msg.body("Welcome! Please enter the company name:")
    elif user_states[sender]['step'] == 'company_name':
        user_states[sender]['company_name'] = incoming_msg
        user_states[sender]['step'] = 'question'
        msg.body(f"Company name set to {incoming_msg}. Now, please enter your question:")
    elif user_states[sender]['step'] == 'question':
        company_name = user_states[sender]['company_name']
        question = incoming_msg
        
        # Generate response using your existing function
        response = generate_response(question, company_name, vectorstore)
        
        msg.body(response)
        
        # Reset the state for this user
        user_states[sender] = {'step': 'company_name'}
        msg.body(response + "\n\nIf you have another question, please start by entering a company name:")

    return str(bot_res)

@app.route('/chat', methods=['POST'])
def chat():
    # incoming_question = request.values.get('Body', '').lower()
    # print("incoming - ", incoming_question)
    data = request.get_json()
    question = data['question']
    company_name = data['company_name']
    # print("question - ", question)
    res = generate_response(question, company_name, vectorstore)
    bot_res = MessagingResponse()
    msg = bot_res.message()
    msg.body(res)
    return str(bot_res)


if __name__ == '__main__':
    # connect to db
    client = create_db_client()
    vectorstore = create_vector_store(client, os.getenv("QDRANT_COLLECTION_NAME"))

    app.run()
    # app.run(port = os.getenv("PORT") or 4000, host="0.0.0.0")