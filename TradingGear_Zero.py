import hmac
import hashlib
import time
import requests
import json

api_key = 'C9EEED2CD1BF2C9810B20C0C1388A10127DF3B3F43E4B5E3FE13ED2530665608'
secret = '98290D2A99D8154FB8DB42896180391B908EF49B93B91EFC7746C1F9C3535187'
timestamp = int(time.time() * 1000)
symbol = "BTCUSDT"
quantity = 0.00025
price = 42860

header = {
    'X-MBX-APIKEY' : api_key  
}

def get_signature(param_str):
    sign = hmac.new(bytes(secret, 'utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return sign

def get_account_information():
    url = 'https://api.commex.com/api/v1/account'
    params = {
        'timestamp' : timestamp,
    }
    param_str = ''
    for key, value in params.items():
        param_str += f"%{key}={value}"
    param_str = param_str[1:]

    params['signature'] = get_signature(param_str)
    response = requests.get(url=url, headers=header, params=params)
    return response.text

# get_account_information()

def open_order(symbol, side, quantity, price):
    url = 'https://api.commex.com/api/v1/order'
    header = {
        'X-MBX-APIKEY' : api_key
    }
    percent = price / 100
    params = {
        'symbol' : symbol,
        'side' : side,
        'type' : 'LIMIT',
        'timeInForce' : 'GTC',
        'quantity' : quantity,
        'timestamp' : timestamp,
        'price' : price + percent
    }
    param_str = ''
    for key, value in params.items():
        param_str += f"&{key}={value}"
    param_str = param_str[1:]
    params['signature'] = get_signature(param_str)
    response = requests.post(url=url, headers=header, params=params)
    print(response.text)

open_order(symbol, 'BUY', quantity, price)
x = json.loads(get_account_information())
symbol = 'BTCUSDT'
for i in x['balances']:
    if i['asset'] == symbol.replace('USDT', ''):
        print(i['free'])
print(x['balances'])
    
open_order(symbol, 'BUY', quantity, price)