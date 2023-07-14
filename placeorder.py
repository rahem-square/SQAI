from square.client import Client
import openai
import numpy as np
import uuid

def is_order(body):
    if not body: 
        return False
    openai.api_key = ''
    resp = openai.Embedding.create(
    input=[body, "I would like to order", "can I order"],
    engine="text-embedding-ada-002")

    embedding_a = resp['data'][0]['embedding']
    embedding_b = resp['data'][1]['embedding']
    embedding_c = resp['data'][2]['embedding']
    similarity_score = np.dot(embedding_a, embedding_b)
    similarity_score2 = np.dot(embedding_a, embedding_c)

    if similarity_score > 0.8 or similarity_score2 > 0.8:
        print(similarity_score, similarity_score2)
        return True
    else:
        return False


client = Client(
  access_token="",
  environment="sandbox"
)

def createOrder():
    idempkey = str(uuid.uuid4())


def createCheckoutLink( name, priceAmount, locID):
    idempkey = str(uuid.uuid4())
    result = client.checkout.create_payment_link(
        body = {
            "idempotency_key": idempkey,
            "quick_pay": {
                "name": name,
                "price_money": {
                    "amount": priceAmount,
                    "currency": "USD"
                },
                "location_id": locID
            }
    }
    )
    return str(result.body["payment_link"]["long_url"])

