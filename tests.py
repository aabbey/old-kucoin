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
import pandas as pd
from tqdm import tqdm

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
api_passphrase = os.getenv('API_PASSPHRASE')
#url = 'https://openapi-sandbox.kucoin.com/api/v1/accounts'
now = int(time.time() * 1000)
str_to_sign = str(now) + 'GET' + c.FEE_ENDPOINT
signature = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
passphrase = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
headers = {
    "KC-API-SIGN": signature,
    "KC-API-TIMESTAMP": str(now),
    "KC-API-KEY": api_key,
    "KC-API-PASSPHRASE": passphrase,
    "KC-API-KEY-VERSION": "2"
}


def tradable_pairs():
    cur_list = requests.get(c.URL + c.SYMBOLS_ENDPOINT).json()['data']
    symbols = []
    for cur in cur_list:
        symbols.append(cur['symbol'])
    return symbols


def trade_fee():
    fee = requests.request('get', c.URL + c.FEE_ENDPOINT, headers=headers).json()
    print(fee)


if __name__ == '__main__':
    trade_fee()