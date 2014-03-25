#!/usr/bin/env python3
import sys
import requests
import os
import json
from subprocess import call
from settings import api_baseurl, api_token

api_url = api_baseurl+"/connect"

if len(sys.argv) < 2:
    print("usage: client-connect.py <config-output-file>")
    exit(1)

path = sys.argv[1]

version = os.environ.get('ccvpn')
if not version:
    print('Cannot read "ccvpn" env var')
    exit(1)

try:
    username = os.environ['common_name']
    trusted_ipv4 = os.environ['trusted_ip']
    remote_vpn_addr = os.environ['ifconfig_pool_remote_ip']
    #trusted_ipv6 = os.environ['trusted_ip6']
except KeyError as e:
    print('Cannot read env: '+str(e))
    exit(1)

headers = {
    'X-Gateway-Token': api_token,
    'X-Gateway-Version': version,
}
data = {
    'username': username,
    'remote_addr': trusted_ipv4,
}
r = requests.post(api_url, headers=headers, data=data)

if r.status_code != 200:
    # We can't contact the API, or the username is invalid.
    print('client-connect error %d: %s' % (r.status_code, r.content))
    exit(1)

try:
    params = json.loads(r.content.decode('utf-8'))
except ValueError as e:
    print('Error decoding client-connect response: '+str(e))
    exit(1)

try:
    config = open(path, 'w')
except (FileNotFoundError, PermissionError) as e:
    print('Failed to open config file for writing: '+str(e))
    exit(1)


def forward_port(arg):
    if not isinstance(arg, list):
        raise ValueError('arg should be a list')
    ports_forwarded = []
    for item in arg:
        proto = item[0]
        port = int(item[1])
        dest = remote_vpn_addr
        cmd = ['iptables',
               '-t', 'nat', '-A', 'PREROUTING', '-i', 'eth0',
               '-p', proto, '--dport', str(port),
               '-j', 'DNAT', '--to', dest]
        call(cmd)
        ports_forwarded.append(proto+':'+str(port))
    return 'push "setenv forwarded_ports %s"'%(','.join(ports_forwarded))

def remote_address(arg):
    addr = arg
    mask = '255.255.255.0'
    return 'ifconfig-push %s %s' % (addr, mask)

param_handlers = {
    'speed_limit': lambda arg: 'shaper %d' % (int(arg)),
    'forward_port': forward_port,
    'openvpn_config': lambda arg: arg,
}


for param, value in params.keys():
    try:
        fn = param_handlers[param]
    except KeyError as e:
        print('Unknown param: '+param)
        continue
    try:
        out = fn(value)
    except Exception as e:
        print('error generating config (%s): %s' % (param, str(e)))
        continue
    config.write(str(out)+'\n')

config.close()
exit(0)


