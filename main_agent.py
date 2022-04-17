import asyncio
import constants as c
import helpers
import timeit
import copy
from kucoin.asyncio import KucoinSocketManager


class Agent:
    def __init__(self, cycle_gains, cycle_products, prod_order_books, cycles_with_product):
        self.prod_order_books = prod_order_books
        self.cycles_with_product = cycles_with_product
        self.cycle_gains = cycle_gains
        self.cycle_products = cycle_products
        self.list_of_gains = []
        self.pos_cycles = []
        self.prev_order_books = copy.deepcopy(prod_order_books)
        self.profit = 0.0
        self.count = 0

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
            await asyncio.sleep(60, loop=loop)

    def update_best_bid_ask(self, product, new_best_bid, new_best_ask, new_best_bid_size, new_best_ask_size):
        self.prev_order_books[product]['bids'][0] = self.prod_order_books[product]['bids'][0].copy()
        self.prev_order_books[product]['asks'][0] = self.prod_order_books[product]['asks'][0].copy()

        self.prod_order_books[product]['bids'][0][0] = float(new_best_bid)
        self.prod_order_books[product]['bids'][0][1] = float(new_best_bid_size)

        self.prod_order_books[product]['asks'][0][0] = float(new_best_ask)
        self.prod_order_books[product]['asks'][0][1] = float(new_best_ask_size)

    def trade_through_cycle(self, cycle, sizes):
        for i, cp in enumerate(self.cycle_products[cycle]):
            c.client.create_market_order(symbol=cp[0], side='buy', size=sizes[i])

    def update_cycle_gains(self, cycles):
        for cycle in cycles:
            gain_ratio, size = helpers.get_gain(cycle, self.cycle_products, self.prod_order_books)
            self.cycle_gains[str(cycle)] = gain_ratio
            self.list_of_gains.append(gain_ratio)
            if gain_ratio > 1:
                earn = (gain_ratio-1) * size * c.TO_USD
                if earn > 0.005:
                    if cycle not in self.pos_cycles:
                        print('positive cycle: ', str(cycle))
                        with open('good_cycles.csv', 'a') as fd:
                            fd.write(f"{cycle[1]},{cycle[2]},")
                        for p in self.cycle_products[str(cycle)]:
                            print(p)
                            print(' previous order book: ')
                            print('     bids: ', self.prev_order_books[p[0]]['bids'][0],
                                  '     asks: ', self.prev_order_books[p[0]]['asks'][0])
                            print(' current order book: ')
                            print('     bids: ', self.prod_order_books[p[0]]['bids'][0],
                                  '     asks: ', self.prod_order_books[p[0]]['asks'][0])
                        print('gain ratio: ', gain_ratio)
                        print('earn score: ', earn)
                        print()
                        self.profit += earn
                        self.pos_cycles.append(cycle)
            else:
                if cycle in self.pos_cycles:
                    self.pos_cycles.remove(cycle)
            if self.count % 100000 == 0:
                print(helpers.stats(self.list_of_gains))
                print(self.profit)
                self.list_of_gains = []
            self.count += 1

    def start_listening(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.listening_for_tickers(loop))