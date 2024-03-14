import requests
import os
import hmac
import argparse
import json
from dotenv import load_dotenv
import os
import signal
import argparse
import secrets
import random
import threading
from datetime import datetime

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
    return response.status_code

def hashtest():
    url = SERVER_URL + '/transaction'
    nonce = secrets.token_bytes(512).hex()
    data = {
        "originAccount": "123456",
        "destinationAccount": "654321",
        "amount": "100",
        "nonce": nonce,
        "hash": "invalid_hash"
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"{response.status_code}: {response.text}")
    



def noncetest():
    print("Ejecutando test de nonce. En el primero, el servidor debe responder con un 200 y el segundo con un 400")
    status = []
    url = SERVER_URL + '/transaction'
    originAccount = "123456"
    destinationAccount = "654321"
    amount = "100"
    nonce = secrets.token_bytes(512).hex()
    for i in [0,1]:
        print(f"Test {i+1}")
        
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
        status.append(response.status_code)
    if status[0] == 200 and status[1] == 400:
        print("Test de nonce exitoso")
    else:
        print("Test de nonce fallido")
    
def multitest(numTest):
    url = SERVER_URL + '/transaction'
    trustworthy_transactions=0
    expected_responses=0
    total_transactions = 0
    originAccount = "test_origin_account"
    destinationAccount = "test_destiny_account"
    amount = "100"
    nonces = []
    for i in range(0,numTest):
        print(f"Test {i+1}")
        prob = random.random()
        if prob < 0.5:
            ''' El 50% de las veces se envía un nonce válido y un hash válido '''
            nonce = secrets.token_bytes(512).hex()
            nonces.append(nonce)
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
            if response.status_code == 200:
                trustworthy_transactions+=1
                expected_responses+=1
            total_transactions+=1

        elif prob < 0.75:
            ''' El 25% de las veces se envía un nonce válido y un hash inválido '''
            nonce = secrets.token_bytes(512).hex()
            data = {
                "originAccount": originAccount,
                "destinationAccount": destinationAccount,
                "amount": amount,
                "nonce": nonce,
                "hash": "invalid_hash"
            }
            headers = {'Content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(data), headers=headers)
            print(f"{response.status_code}: {response.text}")
            if response.status_code == 400 and "Invalid hash" in response.text:
                expected_responses+=1
            total_transactions+=1
            
        else:
            ''' El 25% de las veces se envía primero una transacción válida y se lanza otra con el nonce de la primera'''
            n = random.randint(0,len(nonces)-1)
            nonce = nonces[n]
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
            if response.status_code == 400 and "This transaction is duplicated" in response.text:
                expected_responses+=1
            total_transactions+=1
    
    kpi = trustworthy_transactions / total_transactions            
    print(f"KPI: {kpi}")
    print(f"Porcentaje respuestas esperadas: {expected_responses/total_transactions*100}%")

def loadtest(numTest):
    trustworthy_transactions = 0
    threads = []
    
    def transaction_test():
        response = transaction("test_origin_account", "test_destiny_account", "100")
        if response == 200:
            nonlocal trustworthy_transactions
            trustworthy_transactions += 1
    
    for _ in range(numTest):
        thread = threading.Thread(target=transaction_test)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    kpi = trustworthy_transactions / numTest
    print(f"KPI: {kpi}")
    

if __name__ == "__main__": 
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='tiv-cli')
    parser.add_argument('-t', '--transaction', nargs=3,metavar=('originAccount', 'destinationAccount', 'amount'), help='Transaction: originAccount destinationAccount amount')
    parser.add_argument('-ht', '--hashtest',action="store_true", help='Transaction: originAccount destinationAccount amount')
    parser.add_argument('-nt', '--noncetest',action="store_true", help='Transaction: originAccount destinationAccount amount')
    parser.add_argument('-mt', '--multitest', nargs=1,metavar=('numTest'), help='Transaction: numTest')
    parser.add_argument('-lt', '--loadtest', nargs=1,metavar=('numTest'), help='Make a loadtest in the sistem')
    
    args = parser.parse_args()
    data = vars(args).values()

    if not any(vars(args).values()):
            parser.print_help()
    if args.transaction:
        transaction(*args.transaction)
        exit(1)
    
    if args.hashtest:
        init_date = datetime.now()
        hashtest()
        print("Tiempo de ejecución: ", datetime.now()-init_date)
        exit(1)
    
    if args.noncetest:
        init_date = datetime.now()
        noncetest()
        print("Tiempo de ejecución: ", datetime.now()-init_date)
        exit(1)
    
    if args.multitest:
        init_date = datetime.now()
        multitest(int(args.multitest[0]))
        print("Tiempo de ejecución: ", datetime.now()-init_date)
        exit(1)

    if args.loadtest:
        init_date = datetime.now()
        loadtest(int(args.loadtest[0]))
        print("Tiempo de ejecución: ", datetime.now()-init_date)
        exit(1)

    else:
        parser.print_help()
        exit(1)
    

