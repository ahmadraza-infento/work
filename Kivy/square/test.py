#export SQUARE_SANDBOX_TOKEN="EAAAEKULRUntEUDQcn2-UYjSUyaFMaYfkihAuuk97TfLTF_P7q80i2lMKz39C4Ju"
import os
from unittest import result
from square.client import Client
os.environ["SQUARE_ACCESS_TOKEN"] = "EAAAEKULRUntEUDQcn2-UYjSUyaFMaYfkihAuuk97TfLTF_P7q80i2lMKz39C4Ju"


# for production -> environment='production' some other params -> max_retries=2, timeout=60
sqclient        = Client(access_token=os.environ['SQUARE_ACCESS_TOKEN'], environment='sandbox')
cards_api       = sqclient.cards 
customers_api   = sqclient.customers
payments_api     = sqclient.payments

action = "create_payment"

if action == "list":
    result = cards_api.list_cards()
    if result.is_success():
        print("cards are -> ", result.body)

    elif result.is_error():
        print(result.errors)

elif action == "create_card":
    body = {}
    body['idempotency_key'] = '4935a656-a929-4792-b97c-8848be85c27c'
    body['source_id']       = '' # card number & CVV 
    body['card']            = {}
    body['card']['cardholder_name'] = 'Amelia Earhart'
    body['card']['billing_address'] = {}
    body['card']['billing_address']['address_line_1'] = '500 Electric Ave'
    body['card']['billing_address']['address_line_2'] = 'Suite 600'
    body['card']['billing_address']['locality'] = 'New York'
    body['card']['billing_address']['administrative_district_level_1'] = 'NY'
    body['card']['billing_address']['postal_code'] = '10003'
    body['card']['billing_address']['country'] = 'US'
    body['card']['customer_id'] = 'N1NA0B84JM4WCXYCVKRT4VZ5H0'
    body['card']['reference_id'] = 'user-id-1'

    result = cards_api.create_card(body)

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

elif action == "create_customer":
    body = {}
    body['given_name'] = 'Amelia'
    body['family_name'] = 'Earhart'
    body['email_address'] = 'Amelia.Earhart@example.com'
    body['address'] = {}
    body['address']['address_line_1'] = '500 Electric Ave'
    body['address']['address_line_2'] = 'Suite 600'
    body['address']['locality'] = 'New York'
    body['address']['administrative_district_level_1'] = 'NY'
    body['address']['postal_code'] = '10003'
    body['address']['country'] = 'US'
    body['phone_number'] = '1-212-555-4240'
    body['reference_id'] = 'user-id-1'
    body['note'] = 'a customer'

    result = customers_api.create_customer(body)

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

elif action == "create_payment":
    body = {}
    body['idempotency_key'] = '4935a656-a929-4792-b97c-8848be85c27c'
    body['source_id']       = 'bnon:bank-nonce-insufficient-funds' # card number & CVV 
    body['amount_money']    = {}
    body['amount_money']['amount'] = 500
    body['amount_money']['currency'] = "USD"

    result = payments_api.create_payment(body)

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

