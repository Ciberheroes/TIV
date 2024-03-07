import requests
import os
import hmac
from datetime import date
import argparse
import json
import schedule
from dotenv import load_dotenv
import os
from datetime import datetime
import signal
import argparse
import secrets

load_dotenv()
SERVER_URL = os.getenv("SERVER_URL")
KEY = os.getenv("KEY")

def signal_handler(sig, frame):
    print('Exiting...')
    exit(0)

def transaction(originAccount, destinationAccount, amount):
    url = SERVER_URL + '/transaction'
    nonce = secrets.token_bytes(512).hex()
    data = {
        "originAccount": originAccount,
        "destinationAccount": destinationAccount,
        "amount": amount,
        "nonce": nonce,
        "hash": hmac.new(KEY.encode(), bytes((originAccount+"    "+destinationAccount+"    "+amount+"    "+nonce).encode('utf-8')), "sha256").hexdigest()
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"{response.status_code}: {response.text}")

if __name__ == "__main__": 
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='tiv-cli')
    parser.add_argument('-t', '--transaction', nargs=3,metavar=('originAccount', 'destinationAccount', 'amount'), help='Transaction: originAccount destinationAccount amount')
    parser.add_argument('-ht', '--hashtest', nargs=3,metavar=('originAccount', 'destinationAccount', 'amount'), help='Transaction: originAccount destinationAccount amount')
    parser.add_argument('-nt', '--noncetest', nargs=3,metavar=('originAccount', 'destinationAccount', 'amount'), help='Transaction: originAccount destinationAccount amount')
    parser.add_argument('-mt', '--multitest', nargs=3,metavar=('originAccount', 'destinationAccount', 'amount'), help='Transaction: originAccount destinationAccount amount')
    
    args = parser.parse_args()
    data = vars(args).values()

    if args.transaction:
        transaction(*args.transaction)
        exit(1)
