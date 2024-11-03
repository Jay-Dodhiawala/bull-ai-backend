from flask import Flask, request
from routes.GetResponse import generate_response
from utils.database_utils import create_db_client, create_vector_store
import os
from utils.my_tools import text_splitter
from utils.messaging_utils import send_message, send_template_message
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv

from classes.CustomDictClass import ActiveUserDictionary

load_dotenv()

user_states = ActiveUserDictionary()

app = Flask(__name__)

# Define your prompts
PROMPT_TEMPLATES = {
    "latestresults": """Extract the latest financial results for {company_name} and present it in a well formatted manner. Use Exactly the template below.

Revenue: (JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

Expenses:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

EBITDA:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

PBT:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

PAT:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

Operating Profit Margins:(ONLY PERCENTAGE)
Current Operating Profit Margin: (ONLY PERCENTAGE)
Last Quarter Operating Profit Margin: (ONLY PERCENTAGE)
Last Year Operating Profit Margin: (ONLY PERCENTAGE)

Net Profit Margins:(ONLY PERCENTAGE)
Current Net Profit Margin: (ONLY PERCENTAGE)
Last Quarter Net Profit Margin: (ONLY PERCENTAGE)
Last Year Net Profit Margin:(ONLY PERCENTAGE) """,

    "orderbook": """Extract the latest order book for {company_name}. Present the information in the following format:

Latest Order book value (Date: )
QoQ Growth:
YoY Growth:

Details about the Orderbook:
• 
• 
• 

Additional Information:
- Current Capacity
- Approximate timeline to complete current order book"""
}

STANDARD_PROMPTS = ["latestresults", "orderbook"]

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
        user_states[sender]['step'] = 'list_selection'
        
        # Send instructions first
        send_message(client, sender, f"Company set to: {incoming_msg}\n\nYou can either:\n1. Select from standard prompts below\n2. Type your own question about the company")
        
        # Send the template message with the list picker
        send_template_message(
            client,
            sender,
            'HX623b152c22cb64952ea34cf4d01e71f5',
            None  # Removed parameters
        )
    
    elif user_states[sender]['step'] == 'list_selection':
        company_name = user_states[sender]['company_name']
        
        if incoming_msg in STANDARD_PROMPTS:
            # Handle standard prompts
            prompt = PROMPT_TEMPLATES[incoming_msg].format(company_name=company_name)
            response = generate_response(prompt, company_name, vectorstore)
        else:
            # Handle custom question
            response = generate_response(incoming_msg, company_name, vectorstore)
        
        # Split and send the response
        split_response = text_splitter(response, 1400)
        for doc in split_response:
            send_message(client, sender, doc.page_content)
        
        # Ask if they want to continue
        user_states[sender]['step'] = 'continue_choice'
        send_message(client, sender, "\n\nReply 'yes' to continue or 'no' to start over with a new company.")
    
    elif user_states[sender]['step'] == 'continue_choice':
        if incoming_msg == 'yes':
            user_states[sender]['step'] = 'list_selection'
            send_message(client, sender, f"You can either:\n1. Select from standard prompts below\n2. Type your own question about {user_states[sender]['company_name']}")
            send_template_message(
                client,
                sender,
                'HX623b152c22cb64952ea34cf4d01e71f5',
                None  # Removed parameters
            )
        else:
            user_states[sender] = {'step': 'company_name'}
            send_message(client, sender, "Alright, let's start over. Please enter a new company name:")

    return '', 200

if __name__ == '__main__':
    # connect to db
    db_client = create_db_client()
    vectorstore = create_vector_store(db_client)

    # twilio client
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    app.run(port = os.getenv("PORT") or 4000, host="0.0.0.0")