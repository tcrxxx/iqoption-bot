import numpy as np
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt

def get_sma(prices, rate):
    return prices.rolling(rate).mean()

def get_bollinger_bands(prices, rate=20):
    sma = get_sma(prices, rate)
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2 # Calculate top band
    bollinger_down = sma - std * 2 # Calculate bottom band
    return bollinger_up, bollinger_down

def get_bollinger_bands_candles(candles):
    df = pd.DataFrame(candles)
    df.index = np.arange(df.shape[0])
    closing_prices = df['close']
    bollinger_up, bollinger_down = get_bollinger_bands(closing_prices)

    # plt.title(' Bollinger Bands')
    # plt.xlabel('Days')
    # plt.ylabel('Closing Prices')
    # plt.plot(closing_prices, label='Closing Prices')
    # plt.plot(bollinger_up, label='Bollinger Up', c='g')
    # plt.plot(bollinger_down, label='Bollinger Down', c='r')
    # plt.legend()
    # plt.show()

    return bollinger_up, bollinger_down
    
    # symbol = 'AAPL'
    # df = pdr.DataReader(symbol, 'yahoo')
    # print(df)
    # df.index = np.arange(df.shape[0])
    # closing_prices = df['Close']
    # bollinger_up, bollinger_down = get_bollinger_bands(closing_prices)
    # return bollinger_up, bollinger_down