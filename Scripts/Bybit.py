from datetime import datetime
from datetime import datetime
import requests
import calendar
import pandas as pd
from requests.api import get
import bybit

client = bybit.bybit(test=False, api_key="Your API key Here", api_secret="Your Secret Here")

# Retrieve Recent Price Data
def ticker(pair):
    req = requests.get('https://api.bybit.com/v2/public/tickers?symbol='+pair, headers={'User-Agent':'test'})
    ticker = req.json()['result'][0]

    return {
    'price' : float(ticker['last_price']), 
    'bid' : float(ticker['bid_price']), 
    'ask' : float(ticker['ask_price'])
    }

# Retrieve Last OHLC
def candle_data(timeFrame,pair):
    now = datetime.utcnow()
    unixtime = calendar.timegm(now.utctimetuple())
    start = str(int(unixtime)-60*timeFrame)
    url = 'https://api.bybit.com/v2/public/kline/list?symbol='+pair+'&interval='+str(timeFrame)+'&from='+start
    data = requests.get(url, headers={'User-Agent':'test'}).json()
    data = data['result']

    # The data wasn't retrieved successfully
    if len(data) == 0:
        return False

    time = data[0]['open_time']
    open = data[0]['open']
    high = data[0]['high']
    low = data[0]['low']
    close = data[0]['close']

    return {'time':time,'open':open,'high':high,'low':low,'close':close}
   
# Retrieve previous OHLC candles
def candle_data_history(timeFrame,pair,bars):
    now = datetime.utcnow()
    unixtime = calendar.timegm(now.utctimetuple())
    start = str(int(unixtime)-(bars)*60*timeFrame)
    url = 'https://api.bybit.com/v2/public/kline/list?symbol='+pair+'&interval='+str(timeFrame)+'&from='+start
    data = requests.get(url, headers={'User-Agent':'test'}).json()['result']

    # The data wasn't retrieved successfully
    if len(data) == 0:
        return False

    time = []
    open = []
    high = []
    low = []
    close = []

    # Restructure data into a dataframe
    for i in range(len(data)):
        time.append(float(data[i]['open_time']))    
        open.append(float(data[i]['open']))
        high.append(float(data[i]['high']))
        low.append(float(data[i]['low']))
        close.append(float(data[i]['close']))

    return pd.DataFrame({'time':time,'open':open,'high':high,'low':low,'close':close})

# Retrieve current open positions for a pair
def positions(pair):
    pos = client.Positions.Positions_myPosition(symbol=pair).result()[0]['result']
    if pos == "None": 
        return False
    else:    
        return pos

# Retrieve asset balance 
def GetAssetBalance():
    return client.Wallet.Wallet_getBalance(coin="BTC").result()[0]["result"]['BTC']['wallet_balance'] 

# Enter long
def GoLong(qty, tp, sl):
    print(client.Order.Order_new(symbol="BTCUSD",
    order_type="Market",
    side="Buy",
    qty=qty,
    take_profit=tp,
    stop_loss=sl,
    time_in_force="GoodTillCancel").result())

# Enter short
def GoShort(qty, tp, sl):
    print(client.Order.Order_new(symbol="BTCUSD",
    order_type="Market",
    side="Sell",
    qty=qty,
    take_profit=tp,
    stop_loss=sl,
    time_in_force="GoodTillCancel").result())           