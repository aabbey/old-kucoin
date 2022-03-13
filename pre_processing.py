import helpers
import constants as c
import pandas as pd
from tqdm import tqdm

prod_df = pd.DataFrame.from_dict(c.client.get_symbols())
print(prod_df.keys())
cycles = helpers.get_cycles(prod_df[['baseCurrency', 'quoteCurrency']],
                            start_cur=c.CYCLE_START,
                            cycle_length=c.CYCLE_LEN)
products_list = prod_df['symbol'].tolist()


def instantiate_cycle_gains():
    return dict.fromkeys(map(str, cycles))


def instantiate_cycle_products():
    return dict(zip(map(str, cycles), [helpers.convert_to_cycle_products(c, prod_df) for c in cycles]))


def instantiate_prod_order_books():
    product_obs = {}
    for p in tqdm(products_list):
        ob = c.client.get_order_book(p, depth_20=True)
        if ob['bids'] and ob['asks']:
            product_obs[p] = ob
    return product_obs


def instantiate_cycles_with_product():
    products_in_cycles = dict.fromkeys(products_list)
    for id in products_in_cycles:
        products_in_cycles[id] = []
        for cycle in cycles:
            if (id in "-".join(cycle)) | ("-".join(reversed(id.split("-"))) in "-".join(cycle)):
                products_in_cycles[id].append(cycle)
    return products_in_cycles
