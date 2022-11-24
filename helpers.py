import json
import math
import timeit

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
import csv
import pandas as pd
import uuid


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


def load_df_from_top_curr():
    prod_df = pd.DataFrame.from_dict(c.client.get_symbols())
    use_curr_list = get_common_currencies(c.NUM_CUR)
    prod_dfc = prod_df[prod_df['baseCurrency'].isin(use_curr_list)
                       & prod_df['quoteCurrency'].isin(use_curr_list)]
    return prod_dfc


def get_common_currencies(top):
    with open('good_cycles.csv', 'r') as cycles_file:
        list_of_good_cycles = next(csv.reader(cycles_file))
    d = dict.fromkeys(set(list_of_good_cycles))
    for e in list(set(list_of_good_cycles)):
        d[e] = list_of_good_cycles.count(e)
    df = pd.DataFrame(d.items(), columns=['Currency', 'Occurrences'])
    df = df.sort_values(by='Occurrences', ascending=False, ignore_index=True)
    df_top = df.head(top)
    return df_top['Currency'].to_list()


def get_gain(cycle, cycle_products, prod_orderbooks):
    score = 1.0
    size = c.START_HOLDINGS
    size_multipliers = []
    for i, trade in enumerate(cycle_products[str(cycle)]):
        transaction_cost = trade[2]
        if trade[1]:
            size_multipliers.append(float(prod_orderbooks[trade[0]]['bids'][0][0]))
            score *= (float(prod_orderbooks[trade[0]]['bids'][0][0]) * (1 - transaction_cost))
            prev_size = float(prod_orderbooks[trade[0]]['bids'][0][1])
            next_size = prev_size * float(prod_orderbooks[trade[0]]['bids'][0][0])
            if size > prev_size:
                size = next_size
            else:
                size *= float(prod_orderbooks[trade[0]]['bids'][0][0])
        else:
            size_multipliers.append((1 / float(prod_orderbooks[trade[0]]['asks'][0][0])))
            score *= ((1 / float(prod_orderbooks[trade[0]]['asks'][0][0])) * (1 - transaction_cost))
            next_size = float(prod_orderbooks[trade[0]]['asks'][0][1])
            prev_size = next_size * float(prod_orderbooks[trade[0]]['asks'][0][0])
            if size > prev_size:
                size = next_size
            else:
                size *= 1 / float(prod_orderbooks[trade[0]]['asks'][0][0])

    size_list = [size_multipliers[0] * size] * 3
    for n in range(1, len(size_multipliers)):
        size_list[n] = size_list[n - 1] * size_multipliers[n]
    return score, size, size_list


async def make_trade_from_queue(queue):
    msg = await queue.get()
    print(f"Got {msg}. Posting {msg.symbol=}")
    data = {
        'symbol': msg.symbol,
        'type': 'market',
        'clientOid': str(uuid.uuid4()).replace('-', '')
    }
    if msg.in_order:
        data['funds'] = round(msg.amount, msg.decimal_places)
        data['side'] = 'sell'
    else:
        data['size'] = round(msg.amount, msg.decimal_places)
        data['side'] = 'buy'
    r = await api_endpoints.post_order(data)
    queue.task_done()


def display_expected(cycle, ins, outs):
    print()
    print('----------------Expected-----------------')
    print()
    print("{:<18} {:<23} {:<23} {:<10}".format('Currency', 'in', 'out', 'difference'))
    for curr in cycle:
        print("{:<18} {:<23} {:<23} {:<10}".format(
            curr,
            ins[curr],
            outs[curr],
            ins[curr]-outs[curr]))


def display_order_books(products, order_book, did=None):
    print()
    print('Order Book:')
    print()
    print(did)
    if did:
        print("{:<18} {:<10} {:<15} {:<10} {:<15} {:<10} {:<15}".format('Product', 'Best Bid', 'size', 'Best Ask', 'size', 'did', 'size'))
        for prod in products:
            print("{:<18} {:<10} {:<15} {:<10} {:<15} {:<10} {:<15}".format(
                prod[0],
                float(order_book[prod[0]]['bids'][0][0]),
                float(order_book[prod[0]]['bids'][0][1]),
                float(order_book[prod[0]]['asks'][0][0]),
                float(order_book[prod[0]]['asks'][0][1]),
                did[prod[0]][0],
                did[prod[0]][1]))
    else:
        print("{:<18} {:<10} {:<15} {:<10} {:<15}".format('Product', 'Best Bid', 'size', 'Best Ask', 'size'))
        for prod in products:
            print("{:<18} {:<10} {:<15} {:<10} {:<15}".format(
                prod[0],
                order_book[prod[0]]['bids'][0][0],
                order_book[prod[0]]['bids'][0][1],
                order_book[prod[0]]['asks'][0][0],
                order_book[prod[0]]['asks'][0][1]))


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
                cycle_products.append([prod_df.loc[p]['symbol'], True, 2 * c.TRANSACTION_COST, round(-math.log(float(prod_df.loc[p]['quoteIncrement']), 10))])
            elif cycle[n] in c.LIST_OF_CLASS_C:
                cycle_products.append([prod_df.loc[p]['symbol'], True, 3 * c.TRANSACTION_COST, round(-math.log(float(prod_df.loc[p]['quoteIncrement']), 10))])
            else:
                cycle_products.append([prod_df.loc[p]['symbol'], True, c.TRANSACTION_COST, round(-math.log(float(prod_df.loc[p]['quoteIncrement']), 10))])
        elif '-'.join(reversed(cycle[n:n + 2])) in prod_df.index:
            if cycle[n+1] in c.LIST_OF_CLASS_B:
                cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False, 2 * c.TRANSACTION_COST, round(-math.log(float(prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['baseIncrement']), 10))])
            elif cycle[n+1] in c.LIST_OF_CLASS_C:
                cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False, 3 * c.TRANSACTION_COST, round(-math.log(float(prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['baseIncrement']), 10))])
            else:
                cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False, c.TRANSACTION_COST, round(-math.log(float(prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['baseIncrement']), 10))])
        else:
            print('something wrong with:   ', cycle)
    return cycle_products


def header_setup(endpoint, req_type='', data=''):
    now = int(time.time() * 1000)

    str_to_sign = str(now) + req_type + endpoint + data

    signature = base64.b64encode(
        hmac.new(c.SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(
        hmac.new(c.SECRET.encode('utf-8'), c.PASSPHRASE.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": c.KEY,
        "Content-Type": 'application/json',
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }
    return headers


def trade_fee(symbol):
    headers = header_setup(c.FEE_ENDPOINT_BASE + symbol)
    fees = requests.get(c.URL + c.FEE_ENDPOINT_BASE + symbol, headers=headers).json()
    return fees