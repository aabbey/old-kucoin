from kucoin.client import Client
import os


TRANSACTION_COST = .08
good_gain = -.1

key = os.getenv('API_KEY')
secret = os.getenv('API_SECRET')
passphrase = os.getenv('API_PASSPHRASE')
url = 'https://api.kucoin.com'
ws_url = 'wss://api.kucoin.com'
currency_req = '/api/v1/currencies'
price_req = '/api/v1/prices'
tick = '/api/v1/symbols'
TICKER_ALL = '/market/ticker:all'
orderbook_req = '/api/v1/market/orderbook/level2_20'
client = Client(key, secret, passphrase)