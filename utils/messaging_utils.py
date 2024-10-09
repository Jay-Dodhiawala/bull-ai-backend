def send_message(client, to, body):
    message = client.messages.create(
        body=body,
        from_='whatsapp:+14155238886',
        to=to
    )
    return message.sid