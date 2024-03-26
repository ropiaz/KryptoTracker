# Author: Roberto Piazza
# Date: 25.03.2023

import time
import hmac
import hashlib
import base64
import requests
import urllib.parse
from pathlib import Path
from kryptotracker.models import *
from kryptotracker.utils import *
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


def get_kraken_signature(urlpath, data, secret):
    """Kraken Security"""
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri_path, data, api_key, api_sec):
    """Attaches auth headers and returns results of a POST request"""
    api_url = "https://api.kraken.com"
    headers = {
        'API-Key': api_key,
        'API-Sign': get_kraken_signature(uri_path, data, api_sec)
    }
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


# TODO get api keys
def get_api_data():
    """Return Kraken API key and secret stored in database from user"""
    api_key = None
    api_sec = None
    return api_key, api_sec


def get_kraken_balances(a_key, a_sec):
    """Return kraken balances greater than 0.00005 from kraken api"""
    # Get API data, set nounce
    # api_key, api_sec = get_api_data()
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request(uri_path='/0/private/Balance', data={"nonce": nonce}, api_key=a_key, api_sec=a_sec)
    # remove coins with < 0.00005
    balances = {coin: balance for coin, balance in resp.json()["result"].items() if float(balance) > 1e-05}
    return balances

def get_kraken_staking_data(a_key, a_sec):
    """Return staking data from kraken api"""
    # Get API data, set nounce
    # api_key, api_sec = get_api_data()
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request(uri_path='/0/private/Earn/Allocations', data={
        "nonce": nonce,
        "converted_asset": "EUR",
        "hide_zero_allocations": "true"
    }, api_key=a_key, api_sec=a_sec)
    return resp.json()


def get_kraken_trade_history(a_key, a_sec):
    """Return trade history from kraken api"""
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request('/0/private/TradesHistory', {
        "nonce": nonce
    }, a_key, a_sec)
    return resp.json()['result']


def get_kraken_ledgers_info(a_key, a_sec):
    """Return ledgers info from kraken api"""
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request('/0/private/Ledgers', {
        "nonce": nonce
    }, a_key, a_sec)
    return resp.json()['result']


class Command(BaseCommand):
    help = 'Call exchange APIs, retrieve data and store new data in database'

    def handle(self, *args, **options):
        self.stdout.write('API Request...')
        exchange_apis = ExchangeAPIs.objects.all()
        for exchange_api in exchange_apis:
            user = exchange_api.user
            exchange_name = exchange_api.exchange_name
            api_key = exchange_api.api_key
            api_sec = exchange_api.api_sec
            print(user)
            print(exchange_name)
            print(api_key)
            print(api_sec)
            staking_data = get_kraken_staking_data(a_key=api_key, a_sec=api_sec)
            print(staking_data)
            # ledgers_info = get_kraken_ledgers_info(api_key, api_sec)
            # print(ledgers_info)
