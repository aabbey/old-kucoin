from kucoin.client import Client
import os
import requests


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
FEE_ENDPOINT_BASE = '/api/v1/trade-fees?symbols='
LIST_ACCOUNTS_ENDPOINT = '/api/v1/accounts'
ACCOUNT_LEDGERS_ENDPOINT = '/api/v1/accounts/ledgers?bizType=KCS_Pay_Fees'
HIST_ORDERS_ENDPOINT = '/api/v1/fills'
UNIQUE_ORDER_BASE_ENDPOINT = '/api/v1/orders/'
PRICE_ENDPOINT = '/api/v1/prices'
client = Client(KEY, SECRET, PASSPHRASE)
CYCLE_START = 'ETH'
# TO_USD = 2600
TO_USD = float(requests.get(URL + PRICE_ENDPOINT).json()['data'][CYCLE_START])
CYCLE_LEN = 4
START_HOLDINGS = 100000.0

LIST_OF_CLASS_B = ['1EARTH', '2CRZ', 'ABBC', 'ACA', 'ACE', 'ADS', 'AI', 'AIOZ', 'ALBT', 'ALPACA', 'APL', 'ARKER',
                   'ARRR', 'AURY', 'AXC', 'BASIC', 'BLOK', 'BMON', 'BOA', 'BONDLY', 'BOSON', 'BULL', 'CARD', 'CARR',
                   'CAS', 'CERE', 'CEUR', 'CFG', 'CGG', 'CIRUS', 'CPOOL', 'CQT', 'CREDI', 'CTI', 'CUDOS', 'CUSD',
                   'CWEB', 'CWS', 'DAO', 'DAPPX', 'DFI', 'DFYN', 'DINO', 'DIVI', 'DMTR', 'DORA', 'DPET', 'DPI', 'DPR',
                   'DREAMS', 'DSLA', 'DVPN', 'DYP', 'EDG', 'EFX', 'ELON', 'EQX', 'EQZ', 'ERG', 'ERSDL', 'ETHO',
                   'FALCONS', 'FCL', 'FCON', 'FEAR', 'FLAME', 'FLY', 'FORM', 'FORWARD', 'FRM', 'FRR', 'FTG', 'GAFI',
                   'GALAX', 'GEEQ', 'GENS', 'GGG', 'GHX', 'GLCH', 'GLMR', 'GLQ', 'GMEE', 'GOM2', 'GOVI', 'GSPI',
                   'H3RO3S', 'HAI', 'HAKA', 'HAPI', 'HBB', 'HEART', 'HERO', 'HORD', 'HT', 'HTR', 'HYDRA', 'HYVE',
                   'IDEA', 'ILA', 'IOI', 'ISP', 'JUP', 'KCS', 'KDA', 'KDON', 'KIN', 'KLV', 'KOK', 'KRL', 'LABS',
                   'LACE', 'LAVAX', 'LAYER', 'LIKE', 'LOCG', 'LON', 'LOVE', 'LPOOL', 'LSS', 'LTX', 'MAHA', 'MAKI',
                   'MARS4', 'MARSH', 'MASK', 'MATTER', 'MIR', 'MITX', 'MJT', 'MLK', 'MNET', 'MNST', 'MODEFI', 'MONI',
                   'MOVR', 'MSWAP', 'MTRG', 'MTS', 'NAKA', 'NDAU', 'NGC', 'NGM', 'NIF', 'NORD', 'NTVRK', 'NUM', 'ODDZ',
                   'ONSTON', 'OOE', 'OPUL', 'ORAI', 'ORC', 'OUSD', 'PBR', 'PBX', 'PCX', 'PEL', 'PHNX', 'PLGR', 'PLU',
                   'PMON', 'POL', 'POLC', 'POLK', 'POLX', 'PRQ', 'PUNDIX', 'PYR', 'QI', 'QRDO', 'RACEFI', 'RANKER',
                   'REAP', 'REVU', 'REVV', 'RFOX', 'RLY', 'RMRK', 'RNDR', 'ROAR', 'ROSE', 'ROSN', 'ROUTE', 'SCLP',
                   'SDAO', 'SDN', 'SFUND', 'SHFT', 'SHILL', 'SHX', 'SIENNA', 'SKEY', 'SLIM', 'SOLR', 'SOS', 'SOV',
                   'SPI', 'SRK', 'STARLY', 'STC', 'STND', 'STRONG', 'SURV', 'SWASH', 'SWINGBY', 'SWP', 'TARA', 'TCP',
                   'TIDAL', 'TLOS', 'TOWER', 'TRADE', 'TRVL', 'TXA', 'UFO', 'UMB', 'UNB', 'UNIC', 'UNO', 'UOS', 'VAI',
                   'VEED', 'VEGA', 'VLX', 'VXV', 'WAL', 'WILD', 'WMT', 'WSIENNA', 'XAVA', 'XCAD', 'XCUR', 'XDC', 'XED',
                   'XHV', 'XNL', 'XPRT', 'XSR', 'XTAG', 'XTM', 'YFDAI', 'YLD', 'YOP', 'ZCX', 'ZEE', 'ZKT', 'ZORT']

LIST_OF_CLASS_C = ['BURP', 'CHMB', 'CLH', 'COMB', 'CWAR', 'GARI', 'HOTCROSS', 'IXS', 'LITH', 'MEM', 'NWC', 'PDEX', 'VELO', 'VR']