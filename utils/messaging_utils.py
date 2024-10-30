def send_message(client, to, body):
    message = client.messages.create(
        body=body,
        from_='whatsapp:+14155238886',
        to=to
    )
    return message.sid

def send_template_message(client, to, template_sid, parameters=None):
    """
    Send a template message using Twilio
    
    Args:
        client: Twilio client instance
        to: Recipient's phone number
        template_sid: SID of the template to use
        parameters: Parameters to fill in the template
    """
    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            to=to,
            content_sid=template_sid
        )
        return message.sid
    except Exception as e:
        print(f"Error sending template message: {str(e)}")
        # Fallback to regular message
        return send_message(client, to, 
            "Please select from these options:\n1. latestresults\n2. orderbook\nor type your own question")