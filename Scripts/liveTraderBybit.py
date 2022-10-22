import Bybit as bybit
import pandas_ta as ta
import time
import math

client = bybit.client
print('Logged in Successfully\n')

# Trade Settings
riskReward = 2.1
stopMultiplier = 0.9

# Symbol Settings
timeFrame = 30
pair = "BTCUSD"

# Currently in a trade?
inTrade = False

# Check for entries
def ExecuteCheck():

    # Retrieve candlestick data
    data = bybit.candle_data_history(timeFrame, pair, 100)

    i = len(data)-1  
    close = data['close'][i]
    high = data['high'][i]
    low = data['low'][i]
    balanceUSD = bybit.GetAssetBalance()*close

    # Stochastic RSI settings
    stoc_length = 13
    rsi_length = 20
    band = 15
    k_length = 2
    d_length = 4

    # Exponential Moving averages
    ma = data.ta.ema(length=50)
    ma_slow = data.ta.ema(length=75)

    # Stochastic RSI
    rsi = data.ta.rsi(length=rsi_length)
    stoc = ta.stoch(rsi, rsi, rsi, smooth_k=k_length, k=stoc_length, d=d_length).reset_index()
    atr = data.ta.atr(lenth=14)
    suffix = str(stoc_length)+'_'+str(d_length)+'_'+str(k_length)
    k = stoc['STOCHk_'+suffix]
    d = stoc['STOCHd_'+suffix]
    j = len(k)-1  

    # Stochastic RSI entry conditions
    stoc_long = k[j-1]<d[j-1] and k[j]>d[j] and k[j]<band and d[j]<band
    stoc_short = k[j-1]>d[j-1] and k[j]<d[j] and k[j]>100-band and d[j]>100-band

    # Long entry condition
    if stoc_long and close>ma[i] and close>ma_slow[i] and ma[i]>ma_slow[i] and inTrade == False:

        stopSize = atr[i] * stopMultiplier
        sl = round(low - stopSize, 2)
        shortStopDist = close - sl
        tp = round(close + (shortStopDist * riskReward), 2)

        bybit.GoLong(balanceUSD, tp, sl)
        print(f"Long | {pair} | USD {balanceUSD} | @ ${close} per {pair}")

    # Short entry condition
    if stoc_short and close<ma[i] and close<ma_slow[i] and ma[i]<ma_slow[i] and inTrade == False:
        
        stopSize = atr[i] * stopMultiplier
        sl = round(high + stopSize, 2)
        shortStopDist = sl - close
        tp = round(close - (shortStopDist * riskReward), 2)

        bybit.GoShort(balanceUSD, tp, sl)
        print(f"Short | {pair} | USD {balanceUSD} | @ ${close} per {pair}")

    # Print indicator values
    print(f"\nstochastic long: {stoc_long}")
    print(f"stochastic short: {stoc_short}")
    print(f"fast ema: {ma[i]}")
    print(f"slow ema: {ma_slow[i]}")

startBalance = bybit.GetAssetBalance()

# Check for first candle open
timeOld = bybit.candle_data(timeFrame, pair)['time']
while timeOld == False:
    timeOld = bybit.candle_data(timeFrame, pair)['time']
    print("Get Request Failed, Retrying...")

while True:
    # If new candle open
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

        # Halt program if max account loss is reached
        if bybit.GetAssetBalance()/startBalance < 0.9:
            print("Account Dropped Below 90%")
            break

        # Check for entries    
        ExecuteCheck() 

        print(f"Executed in {round(time.time() - startTime,3)} seconds\n")

