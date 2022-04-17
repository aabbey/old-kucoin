from tqdm import tqdm
import constants as c
import numpy as np
import matplotlib.pyplot as plt
import time
import hmac
import hashlib
import base64
import requests
import api_endpoints


def goes_to(prod_df, cycle, last=False):
    start = cycle[-1]
    new_cycles = []
    if last:
        base_mask = (prod_df['baseCurrency'] == start) & (prod_df['quoteCurrency'] == cycle[0])
        quote_mask = (prod_df['quoteCurrency'] == start) & (prod_df['baseCurrency'] == cycle[0])
        goes_to_list = prod_df['quoteCurrency'][base_mask].to_list() + prod_df['baseCurrency'][quote_mask].to_list()
        for c in goes_to_list:
            new_cycles.append(cycle + [c])
        return new_cycles

    base_mask = prod_df['baseCurrency'] == start
    quote_mask = prod_df['quoteCurrency'] == start
    goes_to_list = prod_df['quoteCurrency'][base_mask].to_list() + prod_df['baseCurrency'][quote_mask].to_list()
    for c in goes_to_list:
        if c not in cycle:
            new_cycles.append(cycle + [c])
    return new_cycles


def get_cycles(prod_df, start_cur, cycle_length):
    level = cycle_length - 2
    cycles = []
    new_cycles = []
    for c in goes_to(prod_df, [start_cur]):
        cycles.append(c)
    for lev in range(level):
        new_cycles = []
        for cycle in tqdm(cycles):
            if lev == level - 1:
                new_cycles = new_cycles + goes_to(prod_df, cycle, True)
            else:
                new_cycles = new_cycles + goes_to(prod_df, cycle)
        cycles = new_cycles
    return new_cycles


def trade_all(curr, pair):
    # error because don't want to trade all all of the time
    if pair[1]:
        for d in api_endpoints.accounts()['data']:
            if d['currency'] == curr and d['type'] == 'trade':
                size = d['balance']
        c.client.create_market_order(symbol=pair[0], side='sell', size=size)
    else:
        for d in api_endpoints.accounts()['data']:
            if d['currency'] == curr and d['type'] == 'trade':
                size = d['balance']
        c.client.create_market_order(symbol=pair[0], side='buy', funds=size)


def get_gain(cycle, cycle_products, prod_orderbooks):
    score = 1.0
    size = c.START_HOLDINGS
    for i, trade in enumerate(cycle_products[str(cycle)]):
        transaction_cost = trade[2]
        if trade[1]:
            score *= (float(prod_orderbooks[trade[0]]['bids'][0][0]) * (1 - transaction_cost))
            prev_size = float(prod_orderbooks[trade[0]]['bids'][0][1])
            next_size = prev_size * float(prod_orderbooks[trade[0]]['bids'][0][0])
            if size > prev_size:
                size = next_size
            else:
                size *= float(prod_orderbooks[trade[0]]['bids'][0][0])
        else:
            score *= ((1 / float(prod_orderbooks[trade[0]]['asks'][0][0])) * (1 - transaction_cost))
            next_size = float(prod_orderbooks[trade[0]]['asks'][0][1])
            prev_size = next_size * float(prod_orderbooks[trade[0]]['asks'][0][0])
            if size > prev_size:
                size = next_size
            else:
                size *= 1 / float(prod_orderbooks[trade[0]]['asks'][0][0])
    return score, size


def stats(gains_list):
    gains_list = np.array(gains_list)
    return np.mean(gains_list), np.std(gains_list), np.max(gains_list), np.min(gains_list)


def plot_gains_hist(gains_list):
    plt.hist(gains_list, bins=50)
    plt.show()


def convert_to_cycle_products(cycle, prod_df):
    cycle_products = []
    prod_df = prod_df.set_index('name')
    for n in range(len(cycle) - 1):
        p = '-'.join(cycle[n:n + 2])
        if p in prod_df.index:
            if cycle[n] in c.LIST_OF_CLASS_B:
                cycle_products.append([prod_df.loc[p]['symbol'], True, 2 * c.TRANSACTION_COST])
            elif cycle[n] in c.LIST_OF_CLASS_C:
                cycle_products.append([prod_df.loc[p]['symbol'], True, 3 * c.TRANSACTION_COST])
            else:
                cycle_products.append([prod_df.loc[p]['symbol'], True, c.TRANSACTION_COST])
        elif '-'.join(reversed(cycle[n:n + 2])) in prod_df.index:
            if cycle[n+1] in c.LIST_OF_CLASS_B:
                cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False, 2 * c.TRANSACTION_COST])
            elif cycle[n+1] in c.LIST_OF_CLASS_C:
                cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False, 3 * c.TRANSACTION_COST])
            else:
                cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False, c.TRANSACTION_COST])
        else:
            print('something wrong with:   ', cycle)
    return cycle_products


def header_setup(endpoint):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + endpoint
    signature = base64.b64encode(
        hmac.new(c.SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(
        hmac.new(c.SECRET.encode('utf-8'), c.PASSPHRASE.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": c.KEY,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }
    return headers


def trade_fee(symbol):
    headers = header_setup(c.FEE_ENDPOINT_BASE + symbol)
    fees = requests.get(c.URL + c.FEE_ENDPOINT_BASE + symbol, headers=headers).json()
    return fees