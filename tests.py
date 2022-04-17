import json
import websockets
import asyncio
import hmac
import hashlib
import time
import api_endpoints
import base64
import matplotlib.pyplot as plt
import pandas as pd
import requests
import constants as c
from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager
import os
import timeit
import helpers
import csv
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

"""
def accounts():
    headers = helpers.header_setup(c.LIST_ACCOUNTS_ENDPOINT)
    accounts = requests.get(c.URL + c.LIST_ACCOUNTS_ENDPOINT, headers=headers).json()
    return accounts"""


def unique_order(id):
    headers = helpers.header_setup(c.UNIQUE_ORDER_BASE_ENDPOINT + id)
    accounts = requests.get(c.URL + c.UNIQUE_ORDER_BASE_ENDPOINT + id, headers=headers).json()
    return accounts


count = {'count': 3}


async def listening(loop):
    async def handle_evt(msg):
        if msg['topic'] == '/account/balance':
            print(msg)
            print(timeit.default_timer())
        # elif msg['topic'] == c.TICKER_ALL:

    ksm = await KucoinSocketManager.create(loop, c.client, handle_evt, private=True)

    await ksm.subscribe('/account/balance')
    while True:
        print('sleeping to keep loop open')
        await asyncio.sleep(10, loop=loop)
        print(timeit.default_timer())
        c.client.create_market_order(symbol='BTC-USDT', side='buy', funds='2.5')


def print_common_currencies(top=40):
    with open('good_cycles.csv', 'r') as cycles_file:
        list_of_good_cycles = next(csv.reader(cycles_file))
    d = dict.fromkeys(set(list_of_good_cycles))
    for e in list(set(list_of_good_cycles)):
        d[e] = list_of_good_cycles.count(e)
    df = pd.DataFrame(d.items(), columns=['Currency', 'Occurrences'])
    df = df.sort_values(by='Occurrences', ascending=False, ignore_index=True)
    print(df.head(top))
    dfh = df.head(top)
    print(dfh['Occurrences'].sum())
    print(df['Occurrences'].sum())


if __name__ == '__main__':
    print_common_currencies()
    """print(api_endpoints.accounts())
    s = timeit.default_timer()
    c.client.create_market_order(symbol='BTC-USDT', side='sell', funds='5')
    c.client.create_market_order(symbol='ETH-USDT', side='buy', funds='5')
    c.client.create_market_order(symbol='ETH-BTC', side='sell', size='.00163')
    total_time = timeit.default_timer() - s
    print(api_endpoints.accounts())
    print(total_time)"""
