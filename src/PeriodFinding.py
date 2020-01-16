"""
This example is copied from https://github.com/ProjectQ-Framework/ProjectQ
and is covered under the Apache 2.0 license.
"""
import os
import time
from getpass import getpass

from quantuminspire.api import QuantumInspireAPI
from quantuminspire.credentials import load_account, get_token_authentication, get_basic_authentication

from src.engines.qi_engine import get_engine
from src.quantum.period_finding import find_period_3, find_period_2

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


def get_authentication():
    """ Gets the authentication for connecting to the Quantum Inspire API."""
    token = load_account()
    if token is not None:
        return get_token_authentication(token)
    else:
        if QI_EMAIL is None or QI_PASSWORD is None:
            print('Enter email:')
            email = input()
            print('Enter password')
            password = getpass()
        else:
            email, password = QI_EMAIL, QI_PASSWORD
        return get_basic_authentication(email, password)


if __name__ == '__main__':
    name = 'TestProjectQ'
    authentication = get_authentication()
    qi_api = QuantumInspireAPI(QI_URL, authentication, project_name=name)

    engine, qi_backend = get_engine(qi_api)

    N = 15

    start = time.time()
    find_period_2(engine, N)
    end = time.time()
    print("Time elapsed:", end - start, "seconds")
