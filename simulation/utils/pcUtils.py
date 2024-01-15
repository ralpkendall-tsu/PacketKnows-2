from django.shortcuts import render
from rest_framework.response import Response
import requests
from requests.auth import HTTPBasicAuth
from ciscoconfparse import CiscoConfParse
from django.conf import settings
from ciscoconfparse.ccp_util import IPv4Obj

def getConfigIP(text):
    # Initialize an empty dictionary to store the parsed data
    parsed_data = {}

    # Split the input text into lines
    lines = text.strip().split('\n')

    # Iterate through each line and parse it
    for line in lines:
        parts = line.strip().split()  # Split each line into words, removing leading/trailing spaces

        # Ensure there are enough parts to process
        if len(parts) >= 2:
            # Handle lines with 'set' keyword (e.g., "set pcname PC1")
            if parts[0] == 'set':
                key = "name"  # The second word is the key
                value = ' '.join(parts[2:])  # Combine the remaining words as the value
                parsed_data[key] = value
            # Handle lines with 'ip' keyword (e.g., "ip 192.168.1.2 192.168.1.1 24")
            elif parts[0] == 'ip' and len(parts) == 3:
                ip_key = 'ip'

                net = str(IPv4Obj(parts[1] + '/' + parts[2]).netmask)

                ip_data = {
                    'ip address': parts[1],
                    'subnet mask': net,
                    'subnet mask in cidr': parts[2]
                }
                parsed_data[ip_key] = ip_data
            elif parts[0] == 'ip' and len(parts) >= 4:
                ip_key = 'ip'

                net = str(IPv4Obj(parts[1] + '/' + parts[3]).netmask)

                ip_data = {
                    'ip address': parts[1],
                    'subnet mask': net,
                    'subnet mask in cidr': parts[3],
                    'default gateway': parts[2]
                }
                parsed_data[ip_key] = ip_data

    return parsed_data