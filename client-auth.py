#!/usr/bin/env python3

"""
This script is called to auth an user on connection or renegotiation.
It POSTs username and password to /api/gateway/auth.
"""

import sys
import os
import requests

from settings import api_baseurl, api_token

api_url = api_baseurl+"/auth"

if len(sys.argv) < 2:
    print("usage: client-auth.py <file>")
    exit(1)

path = sys.argv[1]

version = os.environ.get('ccvpn')
if not version:
    print('Cannot read "ccvpn" env var')
    exit(1)

try:
    creds = open(path, 'r', encoding='utf8')
    lines = [line.strip() for line in creds]
    username = lines[0]
    password = lines[1]
except (FileNotFoundError, PermissionError) as e:
    print('Cannot open %s: %s' % (path, str(e)))
    exit(1)
except IndexError:
    print('Invalid file format')
    exit(1)

headers = {
    'X-Gateway-Token': api_token,
    'X-Gateway-Version': version,
}
data = {
    'username' : lines[0],
    'password' : lines[1],
}

r = requests.post(api_url, headers=headers, data=data)

if r.status_code == 200:
    exit(0)
else:
    exit(1)

