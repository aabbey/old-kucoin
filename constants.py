from kucoin.client import Client
import os


TRANSACTION_COST = .001
GOOD_GAIN = -.25

KEY = os.getenv('API_KEY')
SECRET = os.getenv('API_SECRET')
PASSPHRASE = os.getenv('API_PASSPHRASE')

URL = 'https://api.kucoin.com'
SYMBOLS_ENDPOINT = '/api/v1/symbols'
ws_url = 'wss://api.kucoin.com'
currency_req = '/api/v1/currencies'
price_req = '/api/v1/prices'
L2UPDATE = '/market/level2:MKR-USDT'
TICKER_ALL = '/market/ticker:all'
BTC_USDT_TOP_5 = '/spotMarket/level2Depth5:BTC-USDT'
FEE_ENDPOINT = '/api/v1/trade-fees?symbols=KCS-USDT'
LIST_ACCOUNTS_ENDPOINT = '/api/v1/accounts'
ACCOUNT_LEDGERS_ENDPOINT = '/api/v1/accounts/ledgers?bizType=KCS_Pay_Fees'
HIST_ORDERS_ENDPOINT = '/api/v1/fills'
UNIQUE_ORDER_BASE_ENDPOINT = '/api/v1/orders/'
PRICE_ENDPOINT = '/api/v1/prices'
client = Client(KEY, SECRET, PASSPHRASE)
CYCLE_START = 'ETH'
TO_USD = 2600.0
CYCLE_LEN = 4
START_HOLDINGS = 100000.0