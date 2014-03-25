#!/usr/bin/env python3
import sys
import requests
import os
from settings import api_baseurl, api_token

api_url = api_baseurl+"/disconnect"

version = os.environ.get('ccvpn')
if not version:
    print('Cannot read "ccvpn" env var')
    exit(1)

try:
    username = os.environ['common_name']
    bytes_received = os.environ.get('bytes_received')
    bytes_sent = os.environ.get('bytes_sent')
except KeyError as e:
    print('Cannot read env: '+str(e))
    exit(1)

headers = {
    'X-Gateway-Token': api_token,
    'X-Gateway-Version': version,
}
data = {
    'username': username,
    'bytes_up': bytes_sent,
    'bytes_down': bytes_received,
}
r = requests.post(api_url, headers=headers, data=data)

if r.status_code != 200:
    # We can't contact the API, or the username is invalid.
    print('client-disconnect error: ' % (r.status_code, r.content))
    exit(1)

exit(0)

