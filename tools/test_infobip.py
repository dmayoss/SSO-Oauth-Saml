#!/usr/bin/python

import requests

url = "https://api.infobip.com/api/sendsms/plain"
json_url = "http://api.infobip.com/api/v3/sendsms/json"

infobip_user="username"
infobip_pass="password"

sender="Sender"
recipient="123456789"

message="This is a test message"

payload = {
    'user': infobip_user,
    'password': infobip_user,
    'sender': infobip_user,
    'GSM': recipient,
    'SMSText': message,
    'encoding': 'UTF-8',
}

json_payload = {
    "authentication": {
        "username": infobip_user,
        "password": infobip_pass,
    },
    "messages": [{
        "sender": sender,
        "text": message,
        "recipients": [ { "gsm": recipient } ]
    }]
}

# json
r = requests.post('{}'.format(json_url), json=json_payload)
print(r.json())

# plain
#r = requests.get('{}'.format(url), params=payload4)
#print(r.text)

