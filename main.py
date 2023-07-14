from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import getrestaurant
import placeorder

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    openai.api_key = ''
    """Respond to incoming calls with a simple text message."""
    inf = getrestaurant.getRestaurantInfo()
    info = str(inf)
    listofmenuitems = []
    for item in inf['menu']:
        listofmenuitems.append(item['name'])
    body = request.values.get('Body', None)
    # What is the menu today
    # I'm vegan, what are some options for me
    # Are there tables currently availble

    # body = "Can I order a salmon, 2 lobster, and a soup if you have it?"
    isorder = placeorder.is_order(body)
    if not body:
        body = "What is the menu today?"

    # Start our TwiML response
    resp = MessagingResponse()
    if isorder:
        print('isorder')
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens = 100,
        temperature = 0.01,
        messages=[
            {"role": "assistant", 
             "content": "Context: " + info + "Extract the list of ordered items into a list of tuples in the form (name, number of items ordered):" + body},
            ]
            )
        partial = completion.choices[0].message.content[1:-1].split('(')[1:]
        items = []
        for part in partial:
            item = part.split("'")[1]
            ind = part.index(')')
            number = int(part[ind-1])
            items.append((part.split("'")[1], number))
        a = getrestaurant.makePaymentLink(items)
        print("Preview your order at: " + a)
        resp.message("Preview your order at: " + a)
        return str(resp)
        #prices = placeorder.prices(ls, listofmenuitems)
    # Add a message
    else:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens = 100,
        temperature = 0.01,
        messages=[
            {"role": "assistant", "content": "Context: " + info + "Answer on behalf of the restaurant. Answer this question in at most 3 sentences: " + body},
                ]
        )
        print(completion.choices[0].message)
        resp.message(completion.choices[0].message.content)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
