import pandas as pd
from binance.client import Client
import talib
import numpy as np
from talib import MA_Type
from talib import ADX, RSI, MACD, STOCH
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import time
import math
import telebot
import time
import requests
import hmac
import hashlib
import json
from telebot import types

bot = telebot.TeleBot('6312689394:AAE0wejoCqGdUDprRpXjIc401zCmN21SVl4')

id = 1660691311

api_key = 'C9EEED2CD1BF2C9810B20C0C1388A10127DF3B3F43E4B5E3FE13ED2530665608'
api_secret = '98290D2A99D8154FB8DB42896180391B908EF49B93B91EFC7746C1F9C3535187'

header = {
    'X-MBX-APIKEY' : api_key  
}

def get_signature(param_str):
    sign = hmac.new(bytes(api_secret, 'utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return sign

timestamp = int(time.time() * 1000)
client = Client(api_key, api_secret)
partOfBalance = 11
objects = []
tickets = []
balance_coin = 0
counterProfit = 1 
info = client.futures_exchange_info()

def startTelebot():
    bot.send_message(id, "We start a work, let's see what statistic will be", parse_mode='Markdown')
    
def sendStatistic(statistic, cycle):
    bot.send_message(id, f' Statistic is {str(statistic)}, num of tickets is {str(len(tickets))}, cycle num {cycle}', parse_mode='Markdown')
def sendLose(symbol, balanceQty, ticketQty):
    bot.send_message(id, f'We need to sell this coin {symbol}, balance is {balanceQty}, ticket qty is {ticketQty}')
# def sendSignalToBuy(coin):
#     bot.send_message(id, f'We should buy {coin}')
def sendBought(symbol):
    bot.send_message(id, f'We bought {symbol}')
def sendSold(symbol):
    bot.send_message(id, f"We sold {symbol}")
def sendCantBuy(symbol):
    bot.send_message(id, f"We can't buy coin {symbol}")
def sendWhiteList(whiteList):
    bot.send_message(id, f"White list is {whiteList}")
def sendSellError(coin):
    bot.send_message(id, f"Error in sell in {coin}")
def sendSell(coin):
    bot.send_message(id, f'We in a sell stage {coin}')
def sendTicket(ticket):
    bot.send_message(id, f'Coin is {ticket.symbol[0]} price is {ticket.price[0]} takeprofit is {ticket.takeprofit[0]} stoploss is {ticket.stoploss[0]}')
def sendProfit(ticket):
    bot.send_message(id, f'Profit is of the {ticket.symbol[0]} is {ticket.profit}')
def makeStatistic(i):
    global counterProfit
    for ticket in tickets:
        if hasattr(ord, 'profit'):
            if ticket.profit == True:
                counterProfit += 1
            
    Statistic = len(tickets) / counterProfit
    sendStatistic(Statistic, i)



class coinObject:
    def __init__(self, symbol, dataframe):
        self.symbol = symbol
        self.dataframe = dataframe

class ticket:
    def __init__(self, symbol, price, quantity, step, precision):
        self.symbol = symbol,
        self.price = price,
        self.takeprofit = price + price / 100 * 0.5,
        self.stoploss = price - price / 100 * 0.5,
        self.quantity = quantity,
        self.sold = False,
        self.step = step
        self.precision = precision

def getHistoryData(symbol):
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "2 hours ago UTC")
    historyDataFrame = pd.DataFrame(klines)
    historyDataFrame = historyDataFrame.rename(columns={0 : 'time', 1 : 'Open', 2 : 'High', 3 : 'Low', 4 : 'Close', 5 : 'Volume', 6 : 'Close time', 7 : 'Quote', 8 : 'Number of trades', 9 : 'Taker buy', 10 : 'Taker buy quote', 11 : 'Ignore'})
    historyDataFrame['SMA_50'] = talib.SMA(historyDataFrame['Close'])
    historyDataFrame['SMA_100'] = talib.SMA(historyDataFrame['Close'], 100)
    historyDataFrame['SMA_hist'] = historyDataFrame['SMA_50'] - historyDataFrame['SMA_100']
    historyDataFrame['RSI'] = RSI(historyDataFrame['Close'], timeperiod=14)
    historyDataFrame['MACD'], historyDataFrame['Macdsignal'], historyDataFrame['Macdhist'] = MACD(historyDataFrame['Close'], 12, 26, 9)
    historyDataFrame['MACDDay'], historyDataFrame['MacdsignalDay'], historyDataFrame['MacdhistDay'] = MACD(historyDataFrame['Close'], 360, 720, 81)
    historyDataFrame['STOCH'], historyDataFrame['STOCH_k'] = STOCH(historyDataFrame['Close'], historyDataFrame['High'], historyDataFrame['Low'])
    historyDataFrame['ADX'] = ADX(historyDataFrame['High'], historyDataFrame['Low'], historyDataFrame['Close'], timeperiod = 12)
    historyDataFrame['Close'] = historyDataFrame['Close'].astype(float)
    return historyDataFrame

def getLastMinuteData(symbol):
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 minute ago UTC")
    lastMinutesDataFrame = pd.DataFrame(klines)
    lastMinutesDataFrame = lastMinutesDataFrame.rename(columns={0 : 'time', 1 : 'Open', 2 : 'High', 3 : 'Low', 4 : 'Close', 5 : 'Volume', 6 : 'Close time', 7 : 'Quote', 8 : 'Number of trades', 9 : 'Taker buy', 10 : 'Taker buy quote', 11 : 'Ignore'})
    for object in objects:
        if object.symbol == symbol:
            appendLastMinute(object, lastMinutesDataFrame)
    return lastMinutesDataFrame

def update_dataframe(dataframe):
    dataframe['SMA_50'] = talib.SMA(dataframe['Close'])
    dataframe['SMA_100'] = talib.SMA(dataframe['Close'], 100)
    dataframe['SMA_hist'] = dataframe['SMA_50'] - dataframe['SMA_100']
    dataframe['RSI'] = RSI(dataframe['Close'], timeperiod=14)
    dataframe['MACD'], dataframe['Macdsignal'], dataframe['Macdhist'] = MACD(dataframe['Close'], 12, 26, 9)
    dataframe['MACDDay'], dataframe['MacdsignalDay'], dataframe['MacdhistDay'] = MACD(dataframe['Close'], 360, 720, 81)
    dataframe['STOCH'], dataframe['STOCH_k'] = STOCH(dataframe['Close'], dataframe['High'], dataframe['Low'])
    dataframe['ADX'] = ADX(dataframe['High'], dataframe['Low'], dataframe['Close'], timeperiod = 12)

def Strategy(object):
    global tickets
    coin = object.symbol
    price = float(object.dataframe['Close'].iloc[[-1]].iloc[0])
    percent = price / 100
    rsi = float(object.dataframe['RSI'].iloc[[-1]].iloc[0])
    macdhist = float(object.dataframe['Macdhist'].iloc[[-1]].iloc[0])
    adx = float(object.dataframe['ADX'].iloc[[-1]].iloc[0])
    smaK = float(object.dataframe['SMA_50'].iloc[[-1]].iloc[0])
    sma = float(object.dataframe['SMA_100'].iloc[[-1]].iloc[0])
    percentMacd = float(object.dataframe['Macdhist'].max()) / 100 * 10
    adxmo = float(object.dataframe['ADX'].iloc[[-2]].iloc[0])
    oldmacd = float(object.dataframe['Macdhist'].iloc[[-5]].iloc[0])
    backmacd = float(object.dataframe['Macdhist'].iloc[[-2]].iloc[0])
    if smaK - price >= 0 and macdhist >= -percentMacd and macdhist <= percentMacd and adx > adxmo and oldmacd < percentMacd and backmacd < macdhist:
        buy(object.symbol, price)
    for ticket in tickets:
        if ticket.symbol[0] == coin and ticket.sold[0] == False:
            print(f'symbol is {ticket.symbol[0]} price is {price} buy price is {ticket.price[0]} rsi is {rsi}')
        if ticket.symbol[0] == coin and rsi >= 75 and ticket.sold[0] == False:
            ticket.profit = ticket.quantity[0] * price / (ticket.quantity[0] * ticket.price[0] / 100) - 100
            sell(ticket)

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


def takeprofitMove(ord, percent):
    ord.takeprofit = list(ord.takeprofit)
    ord.takeprofit[0] = ord.takeprofit[0] + percent * 0.1
def stoplossMove(ord, percent):
    ord.stoploss = list(ord.stoploss)
    ord.stoploss[0] = ord.stoploss[0] + percent * 0.1

def get_precision(symbol):
   global precision
   for x in info['symbols']:
       if x['symbol'] == symbol:
         precision = x['quantityPrecision']
         print(type(precision))
         if precision == 0 or precision == None or precision is None:
             precision = float(1)
         else:
            precision = float(precision)
         return precision

def makeObject(symbol):
    object = coinObject(symbol, getHistoryData(symbol))
    objects.append(object)

def appendLastMinute(object, lastMinutesDataFrame):
    object.dataframe = pd.concat([object.dataframe, lastMinutesDataFrame], ignore_index=True)
    update_dataframe(object.dataframe)

def makeWhiteList(coins):
    global whiteList
    whiteList = []
    for coin in coins:
        try:
            result = getHistoryData(coin)
            openPrice = float(result['Close'].iloc[[0]].iloc[0])
            closePrice = float(result['Close'].iloc[[-1]].iloc[0])
            percents = (closePrice / 100)
            if closePrice > openPrice:
                if closePrice - openPrice > percents:
                    whiteList.append(coin)
        except Exception as E:
            continue

def buy(symbol, price):
    global timestamp
    try:
        timestamp = int(time.time() * 1000)
        accountInformation = json.loads(get_account_information())
        print(accountInformation)
        for i in accountInformation['balances']:
            if i['asset'] == 'USDT':
                balance_usdt = float(i['free'])
        quantity = partOfBalance / price
        if balance_usdt > partOfBalance:
            for filt in client.get_symbol_info(symbol)['filters']:
                        if filt['filterType'] == 'LOT_SIZE':
                            step = float(filt['stepSize'])
                            quantity = quantity - (quantity % step)
            precision = get_precision(symbol)
            if precision is None:
                precision = int(1)
            precision = int(precision)
            percent = price / 500
            quantity = float(round(quantity, int(precision)))
            url = 'https://api.commex.com/api/v1/order'
            header = {
                'X-MBX-APIKEY' : api_key
            }
            params = {
                'symbol' : symbol,
                'side' : 'BUY',
                'type' : 'LIMIT',
                'timeInForce' : 'GTC',
                'quantity' : quantity,
                'price' : price,
                'timestamp' : timestamp
            }
            param_str = ''
            for key, value in params.items():
                param_str += f"&{key}={value}"
            param_str = param_str[1:]
            params['signature'] = get_signature(param_str)
            response = requests.post(url=url, headers=header, params=params)
            accountInformation = json.loads(get_account_information())
            for i in accountInformation['balances']:
                if i['asset'] == symbol.replace('USDT', ''):
                    balance_coin = float(i['free'])
            if quantity > balance_coin:
                quantity = quantity - step
            quantity = quantity - quantity % step
            quantity = round(quantity, precision)
            xTicket = ticket(symbol, price, quantity, step, precision)
            tickets.append(xTicket)
            for i in accountInformation['balances']:
                if i['asset'] == symbol.replace('USDT', ''):
                    balance_coin = float(i['free'])
            print(f'Bought {symbol}, balance is {balance_coin}, quantity is {quantity}, step is {step}')
    except Exception as E:
        print(E)

def sell(ticket):
    global timestamp
    try:
        timestamp = int(time.time() * 1000)
        accountInformation = json.loads(get_account_information())
        for i in accountInformation['balances']:
            if i['asset'] == ticket.symbol[0].replace('USDT', ''):
                balance_coin = float(i['free'])
        if ticket.quantity[0] < balance_coin: 
            print(f'ticket quantity is {ticket.quantity[0]}, balance is {balance_coin}')
            url = 'https://api.commex.com/api/v1/order'
            header = {
                'X-MBX-APIKEY' : api_key
            }
            params = {
                'symbol' : ticket.symbol[0],
                'side' : 'SELL',
                'type' : 'MARKET',
                'timeInForce' : 'GTC',
                'quantity' : ticket.quantity[0],
                'timestamp' : timestamp,
            }
            param_str = ''
            for key, value in params.items():
                param_str += f"&{key}={value}"
            param_str = param_str[1:]
            params['signature'] = get_signature(param_str)
            response = requests.post(url=url, headers=header, params=params)
            print('Sold ', ticket.symbol[0])
            ticket.sold = list(ticket.sold)
            ticket.sold[0] = True
        else:
            accountInformation = json.loads(get_account_information())
            for i in accountInformation['balances']:
                if i['asset'] == ticket.symbol[0].replace('USDT', ''):
                    balance_coin = float(i['free'])
            quantity = ticket.quantity[0]
            while balance_coin < quantity:
                quantity = quantity - ticket.step
            print(f'ticket quantity is {ticket.quantity[0]}, qunatity for sell is {quantity}, balance is {balance_coin}')
            url = 'https://api.commex.com/api/v1/order'
            header = {
                'X-MBX-APIKEY' : api_key
            }
            params = {
                'symbol' : ticket.symbol[0],
                'side' : 'SELL',
                'type' : 'MARKET',
                'timeInForce' : 'GTC',
                'quantity' : quantity,
                'timestamp' : timestamp,
            }
            param_str = ''
            for key, value in params.items():
                param_str += f"&{key}={value}"
            param_str = param_str[1:]
            params['signature'] = get_signature(param_str)
            response = requests.post(url=url, headers=header, params=params)
            ticket.sold = list(ticket.sold)
            ticket.sold[0] = True
            print('Sold ', ticket.symbol[0])
            # print(type(ticket.quantity, ticket.quantity[0], ticket.step, ticket.step[0]))
    except Exception as E:
        print(E)
        timestamp = int(time.time() * 1000)
        accountInformation = json.loads(get_account_information())
        for i in accountInformation['balances']:
            if i['asset'] == ticket.symbol[0].replace('USDT', ''):
                balance_coin = float(i['free'])
        quantity = ticket.quantity[0]
        print(f'Error balance is {balance_coin} quantity is {quantity}')
        while balance_coin - ticket.step * 10 < quantity:
            try:        
                quantity = quantity - ticket.step
                print(f"Error with {ticket.symbol[0]} quantity now is {quantity} balance is {balance_coin} try to sell with {round(quantity, ticket.precision)}")
                url = 'https://api.commex.com/api/v1/order'
                header = {
                    'X-MBX-APIKEY' : api_key
                }
                params = {
                    'symbol' : ticket.symbol[0],
                    'side' : 'SELL',
                    'type' : 'MARKET',
                    'timeInForce' : 'GTC',
                    'quantity' : quantity,
                    'timestamp' : timestamp,
                }
                param_str = ''
                for key, value in params.items():
                    param_str += f"&{key}={value}"
                param_str = param_str[1:]
                params['signature'] = get_signature(param_str)
                response = requests.post(url=url, headers=header, params=params)
                break
            except Exception as E:
                print(E)
        ticket.sold = list(ticket.sold)
        ticket.sold[0] = True    
        print('Sold before error ', ticket.symbol[0])


coins = ['BTCUSDT', 'LTCUSDT', 'ETHUSDT', 'NEOUSDT', 'BNBUSDT', 'QTUMUSDT', 'EOSUSDT', 'SNTUSDT', 'BNTUSDT', 'GASUSDT', 'OAXUSDT', 'ZRXUSDT', 'OMGUSDT', 'LRCUSDT', 'TRXUSDT', 'FUNUSDT', 'KNCUSDT', 'XVGUSDT', 'IOTAUSDT', 'LINKUSDT', 'CVCUSDT', 'MTLUSDT', 'NULSUSDT', 'STXUSDT', 'ADXUSDT', 'ETCUSDT', 'ZECUSDT', 'ASTUSDT', 'BATUSDT', 'DASHUSDT', 'POWRUSDT', 'REQUSDT', 'XMRUSDT', 'VIBUSDT', 'ENJUSDT', 'ARKUSDT', 'XRPUSDT', 'STORJUSDT', 'KMDUSDT', 'DATAUSDT', 'MANAUSDT', 'AMBUSDT', 'LSKUSDT', 'ADAUSDT', 'XLMUSDT', 'WAVESUSDT', 'ICXUSDT', 'ELFUSDT', 'RLCUSDT', 'PIVXUSDT', 'IOSTUSDT', 'STEEMUSDT', 'BLZUSDT', 'SYSUSDT', 'ONTUSDT', 'ZILUSDT', 'XEMUSDT', 'WANUSDT', 'LOOMUSDT', 'ZENUSDT', 'THETAUSDT', 'IOTXUSDT', 'QKCUSDT', 'SCUSDT', 'KEYUSDT', 'DENTUSDT', 'IQUSDT', 'ARDRUSDT', 'HOTUSDT', 'VETUSDT', 'DOCKUSDT', 'VTHOUSDT', 'ONGUSDT', 'RVNUSDT', 'DCRUSDT', 'USDCUSDT', 'RENUSDT', 'FETUSDT', 'TFUELUSDT', 'CELRUSDT', 'MATICUSDT', 'ATOMUSDT', 'PHBUSDT', 'ONEUSDT', 'FTMUSDT', 'CHZUSDT', 'COSUSDT', 'ALGOUSDT', 'DOGEUSDT', 'DUSKUSDT', 'ANKRUSDT', 'WINUSDT', 'BANDUSDT', 'HBARUSDT', 'XTZUSDT', 'DGBUSDT', 'NKNUSDT', 'KAVAUSDT', 'ARPAUSDT', 'CTXCUSDT', 'AERGOUSDT', 'BCHUSDT', 'TROYUSDT', 'VITEUSDT', 'FTTUSDT', 'OGNUSDT', 'DREPUSDT', 'WRXUSDT', 'LTOUSDT', 'MBLUSDT', 'COTIUSDT', 'HIVEUSDT', 'STPTUSDT', 'SOLUSDT', 'CTSIUSDT', 'CHRUSDT', 'BTCUPUSDT', 'BTCDOWNUSDT', 'JSTUSDT', 'FIOUSDT', 'STMXUSDT', 'MDTUSDT', 'PNTUSDT', 'COMPUSDT', 'IRISUSDT', 'MKRUSDT', 'SXPUSDT', 'SNXUSDT', 'ETHUPUSDT', 'ETHDOWNUSDT', 'DOTUSDT', 'BNBUPUSDT', 'BNBDOWNUSDT', 'AVAUSDT', 'BALUSDT', 'YFIUSDT', 'ANTUSDT', 'CRVUSDT', 'SANDUSDT', 'OCEANUSDT', 'NMRUSDT', 'LUNAUSDT', 'IDEXUSDT', 'RSRUSDT', 'PAXGUSDT', 'WNXMUSDT', 'TRBUSDT', 'WBTCUSDT', 'KSMUSDT', 'SUSHIUSDT', 'DIAUSDT', 'BELUSDT', 'UMAUSDT', 'WINGUSDT', 'CREAMUSDT', 'UNIUSDT', 'OXTUSDT', 'SUNUSDT', 'AVAXUSDT', 'BURGERUSDT', 'BAKEUSDT', 'FLMUSDT', 'SCRTUSDT', 'XVSUSDT', 'CAKEUSDT', 'ALPHAUSDT', 'ORNUSDT', 'UTKUSDT', 'NEARUSDT', 'VIDTUSDT', 'AAVEUSDT', 'FILUSDT', 'INJUSDT', 'CTKUSDT', 'AUDIOUSDT', 'AXSUSDT', 'AKROUSDT', 'HARDUSDT', 'KP3RUSDT', 'SLPUSDT', 'STRAXUSDT', 'UNFIUSDT', 'CVPUSDT', 'FORUSDT', 'FRONTUSDT', 'ROSEUSDT', 'PROMUSDT', 'SKLUSDT', 'GLMUSDT', 'GHSTUSDT', 'DFUSDT', 'JUVUSDT', 'PSGUSDT', 'GRTUSDT', 'CELOUSDT', 'TWTUSDT', 'REEFUSDT', 'OGUSDT', 'ATMUSDT', 'ASRUSDT', '1INCHUSDT', 'RIFUSDT', 'TRUUSDT', 'DEXEUSDT', 'CKBUSDT', 'FIROUSDT', 'LITUSDT', 'PROSUSDT', 'SFPUSDT', 'FXSUSDT', 'DODOUSDT', 'UFTUSDT', 'ACMUSDT', 'PHAUSDT', 'BADGERUSDT', 'FISUSDT', 'OMUSDT', 'PONDUSDT', 'ALICEUSDT', 'DEGOUSDT', 'BIFIUSDT', 'LINAUSDT']
# makeWhiteList(coins)
whiteList = ['BTCUSDT', 'EOSUSDT', 'SNTUSDT', 'OMGUSDT', 'IOTAUSDT', 'STXUSDT', 'XMRUSDT', 'VIBUSDT', 'XRPUSDT', 'STORJUSDT', 'DATAUSDT', 'MANAUSDT', 'ADAUSDT', 'WAVESUSDT', 'ICXUSDT', 'STEEMUSDT', 'BLZUSDT', 'ONTUSDT', 'ZILUSDT', 'XEMUSDT', 'THETAUSDT', 'QKCUSDT', 'SCUSDT', 'KEYUSDT', 'DENTUSDT', 'VETUSDT', 'RVNUSDT', 'RENUSDT', 'FETUSDT', 'PHBUSDT', 'ONEUSDT', 'FTMUSDT', 'CHZUSDT', 'ALGOUSDT', 'DOGEUSDT', 'DUSKUSDT', 'ANKRUSDT', 'BANDUSDT', 'XTZUSDT', 'DGBUSDT', 'NKNUSDT', 'KAVAUSDT', 'ARPAUSDT', 'AERGOUSDT', 'BCHUSDT', 'TROYUSDT', 'VITEUSDT', 'OGNUSDT', 'WRXUSDT', 'STPTUSDT', 'SOLUSDT', 'CHRUSDT', 'BTCUPUSDT', 'STMXUSDT', 'MDTUSDT', 'SXPUSDT', 'ETHDOWNUSDT', 'DOTUSDT', 'BNBDOWNUSDT', 'YFIUSDT', 'SANDUSDT', 'NMRUSDT', 'LUNAUSDT', 'IDEXUSDT', 'PAXGUSDT', 'WBTCUSDT', 'KSMUSDT', 'DIAUSDT', 'BELUSDT', 'WINGUSDT', 'CREAMUSDT', 'OXTUSDT', 'AVAXUSDT', 'BAKEUSDT', 'FLMUSDT', 'SCRTUSDT', 'NEARUSDT', 'VIDTUSDT', 'FILUSDT', 'INJUSDT', 'STRAXUSDT', 'FRONTUSDT', 'SKLUSDT', 'JUVUSDT', 'GRTUSDT', 'CELOUSDT', 'TWTUSDT', '1INCHUSDT', 'RIFUSDT', 'TRUUSDT', 'CKBUSDT', 'PROSUSDT', 'UFTUSDT', 'BADGERUSDT', 'OMUSDT', 'PONDUSDT', 'LINAUSDT']
whiteList = ['AAVEUSDT', 'ADAUSDT', 'APEUSDT', 'APTUSDT', 'ARBUSDT', 'ATOMUSDT', 'AUCTIONUSDT', 'AUDIOUSDT', 'AVAXUSDT', 'BCHUSDT', 'BNBUSDT', 'BONKUSDT', 'BTCUSDT', 'CAKEUSDT', 'CFXUSDT', 'CGPTUSDT', 'CHZUSDT', 'COMPUSDT', 'CRVUSDT', 'DAIUSDT', 'DOGEUSDT', 'DOTUSDT', 'DYDXUSDT', 'EOSUSDT', 'ETCUSDT', 'ETHUSDT', 'FDUSDUSDT', 'FILUSDT', 'FTMUSDT', 'FXSUSDT', 'GMTUSDT', 'GMXUSDT', 'GRTUSDT', 'IMXUSDT', 'INJUSDT', 'IOTXUSDT', 'JTOUSDT', 'KMDUSDT', 'LDOUSDT', 'LINKUSDT', 'LTCUSDT', 'MATICUSDT', 'MKRUSDT', 'NEARUSDT', 'OPUSDT', 'PENDLEUSDT', 'PEPEUSDT', 'RAYUSDT', 'RDNTUSDT', 'RUNEUSDT', 'SANDUSDT', 'SHIBUSDT', 'SOLUSDT', 'SUIUSDT', 'TOKENUSDT', 'TRXUSDT', 'TWTUSDT', 'UNIUSDT', 'USDCUSDT', 'WAVESUSDT', 'WLDUSDT', 'XLMUSDT', 'XRPUSDT', 'YFIUSDT']
print(f'Len of white list is {len(whiteList)}')

for coin in whiteList:
    try:
        makeObject(coin)
        getLastMinuteData(objects[-1].symbol)
        update_dataframe(objects[-1].dataframe)
    except Exception as E:
        whiteList.remove(coin)

for i in range(1400):
    for object in objects:
        try:
            getLastMinuteData(object.symbol)
            update_dataframe(object.dataframe)
            Strategy(object)
        except Exception as E:
            print(E)
    if i % 60 == 0:
        makeStatistic(i)
    print('Cycle ', i)
    time.sleep(60)