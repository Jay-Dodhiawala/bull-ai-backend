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
            content_sid=template_sid,
            from_='whatsapp:+14155238886',
            to=to
        )
        return message.sid
    except Exception as e:
        print(f"Error sending template message: {str(e)}")
        # Send a generic error message instead of the options
        return send_message(client, to, "I apologize for the technical difficulty. Please try your request again.")

def send_pdf_message(client, to, pdf_url, caption="Here's your company analysis report"):
    """Send a PDF document via WhatsApp"""
    try:
        message = client.messages.create(
            media_url=[pdf_url],
            body=caption,
            from_='whatsapp:+14155238886',
            to=to
        )
        return message.sid
    except Exception as e:
        print(f"Error sending PDF message: {str(e)}")
        return send_message(client, to, "I apologize, but I couldn't send the PDF report. Please try again.")