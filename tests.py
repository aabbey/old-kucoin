import json
import websockets
import asyncio
import hmac
import hashlib
import time
import base64
import requests
import constants as c
from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager
import os
import timeit
import helpers
from tqdm import tqdm

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
api_passphrase = os.getenv('API_PASSPHRASE')
#url = 'https://openapi-sandbox.kucoin.com/api/v1/accounts'


def tradable_pairs():
    cur_list = requests.get(c.URL + c.SYMBOLS_ENDPOINT).json()['data']
    symbols = []
    for cur in cur_list:
        symbols.append(cur['symbol'])
    return symbols


def ledgers():
    headers = helpers.header_setup(c.ACCOUNT_LEDGERS_ENDPOINT)
    ledger = requests.get(c.URL + c.ACCOUNT_LEDGERS_ENDPOINT, headers=headers).json()
    return ledger


def accounts():
    headers = helpers.header_setup(c.LIST_ACCOUNTS_ENDPOINT)
    accounts = requests.get(c.URL + c.LIST_ACCOUNTS_ENDPOINT, headers=headers).json()
    return accounts


def unique_order(id):
    headers = helpers.header_setup(c.UNIQUE_ORDER_BASE_ENDPOINT + id)
    accounts = requests.get(c.URL + c.UNIQUE_ORDER_BASE_ENDPOINT + id, headers=headers).json()
    return accounts


if __name__ == '__main__':
    print(accounts())
    s = timeit.default_timer()
    # c.client.create_market_order(symbol='BTC-USDT', side='sell', size='.000125')
    # c.client.create_market_order(symbol='BTC-USDT', side='buy', size='.000125')
    t = timeit.default_timer() - s
    print(f'order took {t} seconds')
    print(accounts())


