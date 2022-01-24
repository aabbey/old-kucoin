from main_agent import Agent
import pre_processing

async def listen_for_tickers():
    async def handle_evt(msg):
        pass

    ksm = await KucoinSocketManager.create(loop, client, handle_evt)
    await ksm.subscribe(c.TICKER_ALL)
    while True:
        await asyncio.sleep(60, loop=loop)


if __name__ == '__main__':
    cycle_gains = pre_processing.instantiate_cycle_gains()
    cycle_products = pre_processing.instantiate_cycle_products()
    prod_order_books = pre_processing.instantiate_prod_order_books()
    cycles_with_product = pre_processing.instantiate_cycles_with_product()

    trading_agent = Agent(cycle_gains, cycle_products, prod_order_books, cycles_with_product)
    trading_agent.start_listening()

