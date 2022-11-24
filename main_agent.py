import asyncio

import api_endpoints
import constants as c
import helpers
import timeit
import copy
from dataclasses import dataclass
from typing import Optional
from kucoin.asyncio import KucoinSocketManager


@dataclass
class TradeMessage:
    symbol: str
    in_order: bool
    amount: float
    decimal_places: float


class Agent:
    def __init__(self, cycle_gains, cycle_products, prod_order_books, cycles_with_product):
        self.trade_queue = asyncio.Queue()
        self.prod_order_books = prod_order_books
        self.cycles_with_product = cycles_with_product
        self.cycle_gains = cycle_gains
        self.cycle_products = cycle_products
        self.list_of_gains = []
        self.pos_cycles = []
        self.prev_order_books = copy.deepcopy(prod_order_books)
        self.profit = 0.0
        self.count = 0
        self.prev_accounts = {}
        for account in api_endpoints.accounts_syncronous()['data']:
            if account['type'] == 'trade':
                self.prev_accounts[account['currency']] = account['balance']
        print(self.prev_accounts)

    async def main_observation_action_loop(self, loop):
        scanning_task = asyncio.create_task(self.listening_for_tickers(loop))
        display_accounts_task = asyncio.create_task(api_endpoints.accounts())
        n_posting_worker = 3
        posting_tasks = [asyncio.create_task(helpers.make_trade_from_queue(self.trade_queue)) for i in range(n_posting_worker)]
        await scanning_task

    async def listening_for_tickers(self, loop):
        async def handle_evt(msg):
            if msg['subject'] in self.prod_order_books:
                self.update_best_bid_ask(msg['subject'],
                                         msg['data']['bestBid'],
                                         msg['data']['bestAsk'],
                                         msg['data']['bestBidSize'],
                                         msg['data']['bestAskSize'])
                self.update_cycle_gains(self.cycles_with_product[msg['subject']])

        ksm = await KucoinSocketManager.create(loop, c.client, handle_evt)

        await ksm.subscribe(c.TICKER_ALL)
        while True:
            await asyncio.sleep(6, loop=loop)
            a = await api_endpoints.accounts()
            # diffs = []
            # currs = []
            for account in a['data']:
                if account['type'] == 'trade':
                    if float(account['balance']) - float(self.prev_accounts[account['currency']]) != 0:
                        print(account['currency'], self.prev_accounts[account['currency']])
                    # currs.append(account['currency'])
                    # diffs.append(float(account['balance']) - float(self.prev_accounts[account['currency']]))
                        print(float(account['balance']) - float(self.prev_accounts[account['currency']]))
                    self.prev_accounts[account['currency']] = account['balance']


    def update_best_bid_ask(self, product, new_best_bid, new_best_ask, new_best_bid_size, new_best_ask_size):
        self.prev_order_books[product]['bids'][0] = self.prod_order_books[product]['bids'][0].copy()
        self.prev_order_books[product]['asks'][0] = self.prod_order_books[product]['asks'][0].copy()

        self.prod_order_books[product]['bids'][0][0] = float(new_best_bid)
        self.prod_order_books[product]['bids'][0][1] = float(new_best_bid_size)

        self.prod_order_books[product]['asks'][0][0] = float(new_best_ask)
        self.prod_order_books[product]['asks'][0][1] = float(new_best_ask_size)

    def update_cycle_gains(self, cycles):
        for cycle in cycles:
            gain_ratio, size, size_list = helpers.get_gain(cycle, self.cycle_products, self.prod_order_books)
            self.cycle_gains[str(cycle)] = gain_ratio
            self.list_of_gains.append(gain_ratio)
            if gain_ratio > 1 or self.count == (c.NUM_CUR * 100):
                earn = (gain_ratio-1) * size * c.TO_USD
                if earn > c.MIN_EARN or True:

                    if cycle not in self.pos_cycles:
                        outs = {}
                        did = {}
                        print('positive cycle: ', str(cycle))

                        print(size_list)

                        # with open('good_cycles.csv', 'a') as fd:
                        #     fd.write(f"{cycle[1]},{cycle[2]},")
                        for i, p in enumerate(self.cycle_products[str(cycle)]):
                            # trade_msg = TradeMessage(symbol=p[0], in_order=p[1], amount=size_list[i], decimal_places=p[3])
                            # self.trade_queue.put_nowait(trade_msg)
                            print(p)
                            if i < 3:
                                if p[1]:
                                    outs[cycle[i]] = size_list[i] / float(self.prev_order_books[p[0]]['bids'][0][0])
                                    did[p[0]] = [float(self.prev_order_books[p[0]]['bids'][0][0]), size_list[i]]
                                else:
                                    outs[cycle[i]] = size_list[i] * float(self.prev_order_books[p[0]]['asks'][0][0])
                                    did[p[0]] = [float(self.prev_order_books[p[0]]['asks'][0][0]), size_list[i]]
                            print(' previous order book: ')
                            print('     bids: ', self.prev_order_books[p[0]]['bids'][0],
                                  '     asks: ', self.prev_order_books[p[0]]['asks'][0])
                            print(' current order book: ')
                            print('     bids: ', self.prod_order_books[p[0]]['bids'][0],
                                  '     asks: ', self.prod_order_books[p[0]]['asks'][0])
                        print('gain ratio: ', gain_ratio)
                        print('earn score: ', earn)
                        print()
                        helpers.display_expected(cycle=cycle,
                                                 ins={cycle[0]: size_list[-1], cycle[1]: size_list[0], cycle[2]: size_list[1]},
                                                 outs=outs)
                        helpers.display_order_books(self.cycle_products[str(cycle)], self.prod_order_books, did)
                        self.profit += earn
                        self.pos_cycles.append(cycle)
            else:
                if cycle in self.pos_cycles:
                    self.pos_cycles.remove(cycle)
            if self.count == (c.NUM_CUR * 500):
                print(helpers.stats(self.list_of_gains))
                print(self.profit)

                """for i, p in enumerate(self.cycle_products[str(['USDT', 'BTC', 'ETH', 'USDT'])]):
                    # trade_msg = TradeMessage(symbol=p[0], in_order=p[1], amount=size_list[i])
                    # self.trade_queue.put_nowait(trade_msg)
                    print(p)
                    print(' previous order book: ')
                    print('     bids: ', self.prev_order_books[p[0]]['bids'][0],
                          '     asks: ', self.prev_order_books[p[0]]['asks'][0])
                    print(' current order book: ')
                    print('     bids: ', self.prod_order_books[p[0]]['bids'][0],
                          '     asks: ', self.prod_order_books[p[0]]['asks'][0])
                gr = self.cycle_gains[str(['USDT', 'BTC', 'ETH', 'USDT'])]
                print('gain ratio: ', gr)
                print('earn score: ', (gr-1) * 5)
                print()

                amount = 5 * (1 / float(self.prod_order_books['BTC-USDT']['asks'][0][0]))
                trade_msg = TradeMessage(symbol='BTC-USDT', in_order=False, amount=amount, decimal_places=self.cycle_products[str(['USDT', 'BTC', 'ETH', 'USDT'])][0][3])
                self.trade_queue.put_nowait(trade_msg)
                amount *= (1 / float(self.prod_order_books['ETH-BTC']['asks'][0][0]))
                trade_msg = TradeMessage(symbol='ETH-BTC', in_order=False, amount=amount, decimal_places=self.cycle_products[str(['USDT', 'BTC', 'ETH', 'USDT'])][1][3])
                self.trade_queue.put_nowait(trade_msg)
                amount *= float(self.prod_order_books['ETH-USDT']['bids'][0][0])
                trade_msg = TradeMessage(symbol='ETH-USDT', in_order=True, amount=amount, decimal_places=self.cycle_products[str(['USDT', 'BTC', 'ETH', 'USDT'])][2][3])
                self.trade_queue.put_nowait(trade_msg)"""

                self.list_of_gains = []
                self.count = 0
            self.count += 1

    def start_listening(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main_observation_action_loop(loop))