from main_agent import Agent
import pre_processing
import constants as c


if __name__ == '__main__':
    cycle_gains = pre_processing.instantiate_cycle_gains()  # {"cycle": gain_ratio, "cycle": gain_ratio, etc.}
    # print(cycle_gains)
    cycle_products = pre_processing.instantiate_cycle_products()  # {"cycle": [['symbol', in_order, fee, places],...],...}
    # print(cycle_products)
    prod_order_books = pre_processing.instantiate_prod_order_books()  # {'symbol': {'time':..., 'sequence':..., 'bids': [['best_bid', 'size'], ['next_best', 'size'],...], 'asks': [['best_ask', 'size'], ['next_best', 'size'],...]}...}
    # print(prod_order_books)
    cycles_with_product = pre_processing.instantiate_cycles_with_product()  # {'symbol': [[cycle], [cycle],...], ...}
    # print(cycles_with_product)

    trading_agent = Agent(cycle_gains, cycle_products, prod_order_books, cycles_with_product)
    trading_agent.start_listening()
