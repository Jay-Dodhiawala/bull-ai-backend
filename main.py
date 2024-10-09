from flask import Flask, request
from routes.GetResponse import generate_response
from utils.database_utils import create_db_client, create_vector_store, add_documents
import os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/')
def hello_world():
    bot_res = MessagingResponse()
    msg = bot_res.message()
    msg.body("hiiiiiiiiiii")
    return str(bot_res)

@app.route('/test', methods=['POST'])
def hello_world_2():
    bot_res = MessagingResponse()
    msg = bot_res.message()
    msg.body("hiiiiiiiiiii")
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

    app.run(port = os.getenv("PORT") or 4000, host="0.0.0.0")