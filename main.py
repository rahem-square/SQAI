from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""

    body = request.values.get('Body', None)
    if not body:
        body = "What is the menu today?"

    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    openai.api_key = ''
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens = 100,
    messages=[
        {"role": "system", "content": "Pretend you are a Greek restaurant. Answer this question in at most 2 sentences: " + body},
            ]
    )
    print(completion.choices[0].message)
    resp.message(completion.choices[0].message.content)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
