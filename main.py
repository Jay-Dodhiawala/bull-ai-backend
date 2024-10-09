from flask import Flask, request
from routes.GetResponse import generate_response
from utils.database_utils import create_db_client, create_vector_store, add_documents
import os
from utils.my_tools import text_splitter
from utils.messaging_utils import send_message
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv

from classes.CustomDictClass import ActiveUserDictionary

load_dotenv()

user_states = ActiveUserDictionary()
# user_states = {}

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
    
    if sender not in user_states:
        user_states[sender] = {'step': 'company_name'}
        send_message(client, sender, "Welcome! Please enter the company name:")
    elif user_states[sender]['step'] == 'company_name':
        user_states[sender]['company_name'] = incoming_msg
        user_states[sender]['step'] = 'question'
        send_message(client, sender, f"Company name set to {incoming_msg}. Now, please enter your question:")
    elif user_states[sender]['step'] == 'question':
        company_name = user_states[sender]['company_name']
        question = incoming_msg
        
        # Generate response using your existing function
        response = generate_response(question, company_name, vectorstore)

        split_response = text_splitter(response, 1400)

        for doc in split_response:
            send_message(client, sender, doc.page_content)
        
        user_states[sender]['step'] = 'continue_choice'
        send_message(client, sender, "\n\nReply 'yes' to continue or 'no' to start over with a new company.")
    elif user_states[sender]['step'] == 'continue_choice':
        if incoming_msg == 'yes':
            user_states[sender]['step'] = 'question'
            send_message(client, sender, f"Great! Please enter your next question about {user_states[sender]['company_name']}:")
        else:
            user_states[sender] = {'step': 'company_name'}
            send_message(client, sender, "Alright, let's start over. Please enter a new company name:")

    return '', 200



if __name__ == '__main__':
    
    # connect to db
    db_client = create_db_client()
    vectorstore = create_vector_store(db_client, os.getenv("QDRANT_COLLECTION_NAME"))

    # twilio client
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    app.run(host="0.0.0.0")
    # app.run(port = os.getenv("PORT") or 4000, host="0.0.0.0")