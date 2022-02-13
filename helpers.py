from tqdm import tqdm
import constants as c
import numpy as np
import matplotlib.pyplot as plt


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


def get_gain(cycle, cycle_products, prod_orderbooks):
    score = 1.0
    size = c.START_HOLDINGS
    for i, trade in enumerate(cycle_products[str(cycle)]):
        if trade[1]:
            score *= (float(prod_orderbooks[trade[0]]['bids'][0][0]) * (1 - c.TRANSACTION_COST))
            prev_size = float(prod_orderbooks[trade[0]]['bids'][0][1])
            next_size = prev_size * float(prod_orderbooks[trade[0]]['bids'][0][0])
            if size > prev_size:
                size = next_size
            else:
                size *= float(prod_orderbooks[trade[0]]['bids'][0][0])
        else:
            score *= ((1 / float(prod_orderbooks[trade[0]]['asks'][0][0])) * (1 - c.TRANSACTION_COST))
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
            cycle_products.append([prod_df.loc[p]['symbol'], True])
        elif '-'.join(reversed(cycle[n:n + 2])) in prod_df.index:
            cycle_products.append([prod_df.loc['-'.join(reversed(cycle[n:n + 2]))]['symbol'], False])
        else:
            print('something wrong with:   ', cycle)
    return cycle_products