from datetime import datetime
from datetime import datetime
import requests
import calendar
import pandas as pd
from requests.api import get
import bybit

client = bybit.bybit(test=False, api_key="Your API key Here", api_secret="Your Secret Here")

def ticker(pair):
    req = requests.get('https://api.bybit.com/v2/public/tickers?symbol='+pair, headers={'User-Agent':'test'})
    ticker = req.json()['result'][0]
    bid = float(ticker['bid_price'])
    ask = float(ticker['ask_price'])
    price = float(ticker['last_price'])
    return {'price' : price, 'bid' : bid, 'ask' : ask}

def candle_data(timeFrame,pair):
    now = datetime.utcnow()
    unixtime = calendar.timegm(now.utctimetuple())
    start = str(int(unixtime)-60*timeFrame)
    url = 'https://api.bybit.com/v2/public/kline/list?symbol='+pair+'&interval='+str(timeFrame)+'&from='+start
    data = requests.get(url, headers={'User-Agent':'test'}).json()
    data = data['result']

    if len(data) == 0:
        return False

    data = data[0]

    time = data['open_time']
    open = data['open']
    high = data['high']
    low = data['low']
    close = data['close']

    return {'time':time,'open':open,'high':high,'low':low,'close':close}
   

def candle_data_history(timeFrame,pair,bars):
    now = datetime.utcnow()
    unixtime = calendar.timegm(now.utctimetuple())
    start = str(int(unixtime)-(bars)*60*timeFrame)
    url = 'https://api.bybit.com/v2/public/kline/list?symbol='+pair+'&interval='+str(timeFrame)+'&from='+start
    data = requests.get(url, headers={'User-Agent':'test'}).json()['result']

    if len(data) == 0:
        return False

    time = []
    open = []
    high = []
    low = []
    close = []

    for i in range(len(data)):
        time.append(float(data[i]['open_time']))    
        open.append(float(data[i]['open']))
        high.append(float(data[i]['high']))
        low.append(float(data[i]['low']))
        close.append(float(data[i]['close']))

    return pd.DataFrame({'time':time,'open':open,'high':high,'low':low,'close':close})

def positions(pair):
    pos = client.Positions.Positions_myPosition(symbol=pair).result()[0]['result']
    if pos == "None": 
        return False
    else:    
        return pos