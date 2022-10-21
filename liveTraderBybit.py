import Bybit as bybit
import pandas_ta as ta
import time
import math

client = bybit.client
print('Logged in Successfully\n')

info = client.Market.Market_symbolInfo().result()
keys = info[0]['result']

# Trade Settings
riskReward = 2.1
stopMultiplier = 0.9

timeFrame = 30
pair = "BTCUSD"

inTrade = False

def GetAssetBalance():
    return client.Wallet.Wallet_getBalance(coin="BTC").result()[0]["result"]['BTC']['wallet_balance']

def GoLong(qty, tp, sl):
    print(client.Order.Order_new(symbol="BTCUSD",
    order_type="Market",
    side="Buy",
    qty=qty,
    take_profit=tp,
    stop_loss=sl,
    time_in_force="GoodTillCancel").result())

def GoShort(qty, tp, sl):
    print(client.Order.Order_new(symbol="BTCUSD",
    order_type="Market",
    side="Sell",
    qty=qty,
    take_profit=tp,
    stop_loss=sl,
    time_in_force="GoodTillCancel").result())

def ExecuteCheck():

    data = bybit.candle_data_history(timeFrame, pair, 100)

    i = len(data)-1  
    close = data['close'][i]
    high = data['high'][i]
    low = data['low'][i]
    balanceUSD = GetAssetBalance()*close

    stoc_length = 13
    rsi_length = 20
    band = 15
    k_length = 2
    d_length = 4

    # Indicators
    ma = data.ta.ema(length=50)
    ma_slow = data.ta.ema(length=75)

    rsi = data.ta.rsi(length=rsi_length)
    stoc = ta.stoch(rsi, rsi, rsi, smooth_k=k_length, k=stoc_length, d=d_length).reset_index()
    atr = data.ta.atr(lenth=14)
    suffix = str(stoc_length)+'_'+str(d_length)+'_'+str(k_length)
    k = stoc['STOCHk_'+suffix]
    d = stoc['STOCHd_'+suffix]
    j = len(k)-1  

    stoc_long = k[j-1]<d[j-1] and k[j]>d[j] and k[j]<band and d[j]<band
    stoc_short = k[j-1]>d[j-1] and k[j]<d[j] and k[j]>100-band and d[j]>100-band

    if stoc_long and close>ma[i] and close>ma_slow[i] and ma[i]>ma_slow[i] and inTrade == False:

        stopSize = atr[i] * stopMultiplier
        sl = round(low - stopSize, 2)
        shortStopDist = close - sl
        tp = round(close + (shortStopDist * riskReward), 2)

        GoLong(balanceUSD, tp, sl)
        print(f"Long | {pair} | USD {balanceUSD} | @ ${close} per {pair}")

    if stoc_short and close<ma[i] and close<ma_slow[i] and ma[i]<ma_slow[i] and inTrade == False:
        
        stopSize = atr[i] * stopMultiplier
        sl = round(high + stopSize, 2)
        shortStopDist = sl - close
        tp = round(close - (shortStopDist * riskReward), 2)

        GoShort(balanceUSD, tp, sl)
        print(f"Short | {pair} | USD {balanceUSD} | @ ${close} per {pair}")

    print(f"\nstochastic long: {stoc_long}")
    print(f"stochastic short: {stoc_short}")
    print(f"fast ema: {ma[i]}")
    print(f"slow ema: {ma_slow[i]}")

startBalance = GetAssetBalance()

# Check for New Candle Open
timeOld = bybit.candle_data(timeFrame, pair)['time']
while timeOld == False:
    timeOld = bybit.candle_data(timeFrame, pair)['time']
    print("Get Request Failed, Retrying...")

while True:

    if math.floor(time.time()) - math.floor(timeOld) >= timeFrame*60:
        startTime = time.time()

        # Get Current Candle Open Time
        timeOld = math.floor(time.time())

        # Check if in trade
        if inTrade:
            pos = bybit.positions(pair)
            if pos == None: 
                inTrade = False
            print("In a trade")      

        if GetAssetBalance()/startBalance < 0.9:
            print("Account Dropped Below 90%")
            break

        ExecuteCheck() 
        print(f"Executed in {round(time.time() - startTime,3)} seconds\n")

