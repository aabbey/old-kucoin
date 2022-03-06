from kucoin.client import Client
import os


TRANSACTION_COST = .0008
GOOD_GAIN = -.25

key = os.getenv('API_KEY')
secret = os.getenv('API_SECRET')
passphrase = os.getenv('API_PASSPHRASE')
URL = 'https://api.kucoin.com'
SYMBOLS_ENDPOINT = '/api/v1/symbols'
ws_url = 'wss://api.kucoin.com'
currency_req = '/api/v1/currencies'
price_req = '/api/v1/prices'
L2UPDATE = '/market/level2:MKR-USDT'
TICKER_ALL = '/market/ticker:all'
BTC_USDT_TOP_5 = '/spotMarket/level2Depth5:BTC-USDT'
FEE_ENDPOINT = '/api/v1/base-fee'
client = Client(key, secret, passphrase)
CYCLE_START = 'ETH'
TO_USD = 2600.0
CYCLE_LEN = 4
START_HOLDINGS = 100000.0