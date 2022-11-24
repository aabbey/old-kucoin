import json
import uuid

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


class TestAgent:
    def __init__(self):
        self.between_ticks = []
        self.last = timeit.default_timer()

    async def time_taker(self):
        for i in range(200000000):
            i = 3

    async def listening(self, loop):
        async def handle_evt(msg):
            t = timeit.default_timer()
            t_since_last = t - self.last
            self.between_ticks.append(t_since_last)
            self.last = t

        ksm = await KucoinSocketManager.create(loop, c.client, handle_evt)

        await ksm.subscribe(c.TICKER_ALL)
        while True:
            await asyncio.sleep(5, loop=loop)
            await self.time_taker()
            print(helpers.stats(self.between_ticks[1000:1100]))
            print(len(self.between_ticks))

    def start_listening(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.listening(loop))


async def trade_f(sym, side, f):
    c.client.create_market_order(symbol=sym, side=side, funds=f)


async def trade_s(sym, side, s):
    c.client.create_market_order(symbol=sym, side=side, size=s)


if __name__ == '__main__':
    helpers.display_expected(cycle=['first', 'second', 'third'],
                             ins={'first': 8.4, 'second': .022, 'third': 13.54},
                             outs={'first': 8.3, 'second': .021, 'third': 13.55})
