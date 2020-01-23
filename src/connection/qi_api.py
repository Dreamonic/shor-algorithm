import os
from getpass import getpass

from quantuminspire.api import QuantumInspireAPI
from quantuminspire.credentials import get_token_authentication, load_account, get_basic_authentication

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


def get_authentication_alt():
    """ Gets the authentication for connecting to the Quantum Inspire API."""
    token = load_account()
    if token is not None:
        return get_token_authentication(token)
    else:
        print('Enter email:')
        email = input()
        print('Enter password')
        password = getpass()
        return get_basic_authentication(email, password)


def get_authentication():
    """ Gets the authentication for connecting to the Quantum Inspire API."""
    token = os.getenv('QI_TOKEN')
    if token is not None:
        return get_token_authentication(token)
    return None


def get_api_session():
    return QuantumInspireAPI(QI_URL, get_authentication())
