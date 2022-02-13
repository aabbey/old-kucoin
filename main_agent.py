import asyncio
import constants as c
import helpers
from kucoin.asyncio import KucoinSocketManager


class Agent:
    def __init__(self, cycle_gains, cycle_products, prod_order_books, cycles_with_product):
        self.prod_order_books = prod_order_books
        self.cycles_with_product = cycles_with_product
        self.cycle_gains = cycle_gains
        self.cycle_products = cycle_products
        self.list_of_gains = []
        self.count = 0

    async def listening_for_tickers(self, loop):
        async def handle_evt(msg):
            if msg['subject'] in self.prod_order_books:
                self.update_best_bid_ask(msg['subject'], msg['data']['bestBid'], msg['data']['bestAsk'])
                self.update_cycle_gains(self.cycles_with_product[msg['subject']])

        ksm = await KucoinSocketManager.create(loop, c.client, handle_evt)
        await ksm.subscribe(c.TICKER_ALL)
        while True:
            await asyncio.sleep(60, loop=loop)

    def update_best_bid_ask(self, product, new_best_bid, new_best_ask):
        if product in self.prod_order_books:
            self.prod_order_books[product]['bids'][0][0] = float(new_best_bid)
        if product in self.prod_order_books:
            self.prod_order_books[product]['asks'][0][0] = float(new_best_ask)

    def update_cycle_gains(self, cycles):
        for cycle in cycles:
            gain_ratio, size = helpers.get_gain(cycle, self.cycle_products, self.prod_order_books)
            self.cycle_gains[str(cycle)] = gain_ratio
            self.list_of_gains.append(gain_ratio)
            if gain_ratio > .9983:
                print(gain_ratio, size * 42000.0)
                print('Earnings:   ', (gain_ratio-1) * size * 42000.0)
            if self.count % 10000 == 0:
                print(helpers.stats(self.list_of_gains))
                # helpers.plot_gains_hist(self.list_of_gains)
                self.list_of_gains = []
            self.count += 1

    def start_listening(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.listening_for_tickers(loop))