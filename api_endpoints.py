import json
import aiohttp
import helpers
import requests
import httpx
import constants as c


async def accounts():
    async with httpx.AsyncClient() as client:
        headers = helpers.header_setup(c.LIST_ACCOUNTS_ENDPOINT, 'GET')
        accounts = await client.get(c.URL + c.LIST_ACCOUNTS_ENDPOINT, headers=headers)
        accounts = accounts.json()
    return accounts


async def post_order(data):
    async with httpx.AsyncClient() as client:
        data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        headers = helpers.header_setup(c.ORDERS_ENDPOINT, 'POST', data=data)
        #data = json.dumps(data)  #, separators=(',', ':'), ensure_ascii=False)
        r = await client.post(c.URL + c.ORDERS_ENDPOINT, data=data, headers=headers, timeout=10)
        print(vars(r))
        print(dir(r))
    return r
