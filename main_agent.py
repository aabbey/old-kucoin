import asyncio
import constants as c
from kucoin.asyncio import KucoinSocketManager

class Agent:
    def __init__(self, cycle_gains, cycle_products, prod_order_books, cycles_with_product):
        self.prod_order_books = prod_order_books
        self.cycles_with_product = cycles_with_product
        self.cycle_gains = cycle_gains
        self.cycle_products = cycle_products

    async def listening_for_tickers(self, loop):
        async def handle_evt(msg):
            self.update_order_book()

        ksm = await KucoinSocketManager.create(loop, c.client, handle_evt)
        await ksm.subscribe(c.TICKER_ALL)
        while True:
            await asyncio.sleep(60, loop=loop)

    def update_order_book(self, product, order):
        pass

    def start_listening(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.listening_for_tickers(loop))