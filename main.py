from flask import Flask, request
from routes.GetResponse import generate_response
from utils.database_utils import create_db_client, create_vector_store
import os
import logging
import requests
from utils.my_tools import text_splitter
from utils.messaging_utils import send_message, send_template_message
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from services.google_slides.slides_generator import GoogleSlidesGenerator
from dotenv import load_dotenv
from pathlib import Path
from classes.CustomDictClass import ActiveUserDictionary
from prompts import PROMPT_TEMPLATES, STANDARD_PROMPTS

# Set up minimal logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

user_states = None
slides_generator = None

app = Flask(__name__)

def initialize_states():
    global user_states
    user_states = ActiveUserDictionary()

@app.route('/')
def hello_world():
    bot_res = MessagingResponse()
    msg = bot_res.message()
    msg.body("Welcome to Indian Markets Bot!")
    return str(bot_res)

@app.route('/', methods=['POST'])
def handle_message():
    incoming_msg = request.form['Body'].strip().lower()
    sender = request.form['From']
    
    if sender not in user_states:
        user_states[sender] = {'step': 'initial_choice'}
        send_template_message(
            client,
            sender,
            'HX16d57a43b1da4022f5cac07226f14e6b',
            None
        )
    
    elif user_states[sender]['step'] == 'initial_choice':
        if incoming_msg in ['company', 'specific company']:
            user_states[sender]['step'] = 'company_name'
            send_message(client, sender, "Please enter the company name:")
        elif incoming_msg in ['general', 'general question']:
            user_states[sender]['step'] = 'general_question'
            send_message(client, sender, "What would you like to know about the Indian markets?")
        else:
            send_message(client, sender, "Please choose either 'company' for specific company analysis or 'general' for market-wide questions.")
    
    elif user_states[sender]['step'] == 'general_question':
        if incoming_msg == 'company':
            user_states[sender]['step'] = 'company_name'
            send_message(client, sender, "Please enter the company name:")
        else:
            try:
                response = generate_response(incoming_msg, None, vectorstore)
                split_response = text_splitter(response, 1400)
                for doc in split_response:
                    send_message(client, sender, doc.page_content)
                # Send template message after successful response
                send_template_message(
                    client,
                    sender,
                    'HXba7ea9a0c5fd3d0c25bdd922593394f6',
                    None
                )
                user_states[sender]['step'] = 'continue_choice'
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                send_message(client, sender, "I apologize, but I encountered an error processing your request. Please try again.")
    
    elif user_states[sender]['step'] == 'company_name':
        company_name = incoming_msg
        user_states[sender]['company_name'] = company_name
        user_states[sender]['step'] = 'list_selection'
        send_message(client, sender, f"Company set to: {company_name}")
        send_template_message(
            client,
            sender,
            'HX4db0e22ee90f7a8236dcd3badcc4b44f',
            None
        )
    
    elif user_states[sender]['step'] == 'list_selection':
        company_name = user_states[sender]['company_name']
        
        if incoming_msg in STANDARD_PROMPTS:
            try:
                prompt = PROMPT_TEMPLATES[incoming_msg].format(company_name=company_name)
                response = generate_response(prompt, company_name, vectorstore)
                split_response = text_splitter(response, 1400)
                for doc in split_response:
                    send_message(client, sender, doc.page_content)
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                send_message(client, sender, "I apologize, but I encountered an error processing your request. Please try again.")
        else:
            try:
                response = generate_response(incoming_msg, company_name, vectorstore)
                split_response = text_splitter(response, 1400)
                for doc in split_response:
                    send_message(client, sender, doc.page_content)
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                send_message(client, sender, "I apologize, but I encountered an error processing your request. Please try again.")
        
        send_template_message(
            client,
            sender,
            'HXba7ea9a0c5fd3d0c25bdd922593394f6',
            None
        )
        user_states[sender]['step'] = 'continue_choice'
    
    elif user_states[sender]['step'] == 'continue_choice':
        if incoming_msg in ['change', 'change company', 'new company']:
            user_states[sender] = {'step': 'initial_choice'}
            send_template_message(
                client,
                sender,
                'HX16d57a43b1da4022f5cac07226f14e6b',
                None
            )
        else:
            if 'company_name' in user_states[sender]:
                user_states[sender]['step'] = 'list_selection'
                send_template_message(
                    client,
                    sender,
                    'HX4db0e22ee90f7a8236dcd3badcc4b44f',
                    None
                )
            else:
                user_states[sender]['step'] = 'general_question'
                send_message(client, sender, "What would you like to know about the Indian markets?")

    return '', 200

if __name__ == '__main__':
    db_client = create_db_client()
    vectorstore = create_vector_store(db_client)

    # Initialize states
    initialize_states()

    # twilio client
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    slides_generator = GoogleSlidesGenerator()
    app.run(port = os.getenv("PORT") or 4000, host="0.0.0.0")
    #app.run(host="0.0.0.0")