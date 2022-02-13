from main_agent import Agent
import pre_processing
import constants as c


if __name__ == '__main__':
    cycle_gains = pre_processing.instantiate_cycle_gains()
    cycle_products = pre_processing.instantiate_cycle_products()
    prod_order_books = pre_processing.instantiate_prod_order_books()
    cycles_with_product = pre_processing.instantiate_cycles_with_product()

    trading_agent = Agent(cycle_gains, cycle_products, prod_order_books, cycles_with_product)
    trading_agent.start_listening()
