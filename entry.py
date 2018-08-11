import ccxt
import structlog
import sys
import time
import numpy as np
import logs
from configuration import Config
from exchange import ExchangeInterface
from exchangedata import ExchangeDataUtil
from talib import abstract
import talib
from datetime import datetime
from indicators.macd import  MACD

import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
from collections import namedtuple
from datetime import datetime
from adviser import Adviser
# g_sp382_stats=None
# g_sp618_stats=None
# g_sp382=None
# g_sp618=None

def ana1():
    inputs = {
        'timestamp' : datetime.now(),
        'open': np.random.random(6),
        'high': np.random.random(6),
        'low': np.random.random(6),
        'close': np.random.random(6),
        'volume': np.random.random(6)
    }
    MACD = abstract.MACD
    output = MACD(inputs,
         fastperiod=6, slowperiod=12, signalperiod=9)
    output1 = ExchangeDataUtil.convert_to_dataframe(output)
    print(output1)

def ana(historicalData):
    dataFrame = ExchangeDataUtil.convert_to_dataframe(historicalData)
    macd_values = abstract.MACD(dataFrame).iloc[:]
    talib.MACD()
    macd_values.dropna(how='all', inplace=True)
    signal = ['macd']
    hot_thresh= 0
    cold_thresh = 0
    if macd_values[signal[0]].shape[0]:
        macd_values['is_hot'] = macd_values[signal[0]] > hot_thresh
        macd_values['is_cold'] = macd_values[signal[0]] < cold_thresh
    return macd_values;

def convertDate(historicalData):
    df = pd.DataFrame(historicalData)
    # df = pd.read_json(file_name, orient='values')
    df.transpose()
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df['datetime'] = df.timestamp.apply(
        lambda x: pd.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
    )
    df['dateweek'] = df.datetime.dt.weekday
    df['ptc'] = df.close.pct_change() * 100

    d = [(price1) for price1 in df.close[:-1]]
    d.insert(0, 0)
    df['preclose'] = d
    df.set_index('datetime', inplace=True, drop=True)
    df.drop('timestamp', axis=1, inplace=True)
    df.fillna(0, inplace=True)
    return df
def calcGoldenStats(df):
    sp382_stats = stats.scoreatpercentile(df.close, 38.2)
    sp618_stats = stats.scoreatpercentile(df.close, 61.8)
    print('统计上的382:' + str(round(sp382_stats, 8)))
    print('统计上的618:' + str(round(sp618_stats, 8)))

    cs_max = df.close.max()
    cs_min = df.close.min()
    sp382 = (cs_max - cs_min) * 0.382 + cs_min
    sp618 = (cs_max - cs_min) * 0.618 + cs_min
    print('视觉上的382:' + str(round(sp382, 8)))
    print('视觉上的618:' + str(round(sp618, 8)))
    r = namedtuple('golden',['sp382_stats','sp618_stats','sp382','sp618'])(sp382_stats,sp618_stats,sp382,sp618)
    return r
def plot_golden(df):

    r = calcGoldenStats(df)

    above618 = np.maximum(r.sp618, r.sp618_stats)
    below618 = np.minimum(r.sp618, r.sp618_stats)
    above382 = np.maximum(r.sp382, r.sp382_stats)
    below382 = np.minimum(r.sp382, r.sp382_stats)


    plt.plot(df.close)
    plt.axhline(r.sp382, c='r')
    plt.axhline(r.sp382_stats, c='m')
    plt.axhline(r.sp618, c='g')
    plt.axhline(r.sp618_stats, c='k')
    plt.fill_between(df.index, above618, below618, alpha=0.5, color='r')
    plt.fill_between(df.index, above382, below382, alpha=0.5, color='g')
    plt.show()

def main():
    # load all config
    config = Config()
    settings = config.settings;

    logs.configure_logging(settings['log_level'], settings['log_mode'])
    logger = structlog.get_logger()
    exchange_interface = ExchangeInterface(config.exchanges)
    adviser = Adviser(config,exchange_interface)

    # # markedPairs = settings['market_pairs'];
    # # exchanges = config.exchanges;
    # historicalData = exchange_interface.get_historical_data(settings['market_pairs'][0], 'bittrex', '30m',None,48)
    # df = convertDate(historicalData)
    # plot_golden(df)
    # macd = MACD().analyze(historicalData,None,0,0)
    # logger.loggerinfo(historicalData)
    # ana1()

    while True:
        adviser.work()
        logger.info("Sleeping for %s seconds", settings['update_interval'])
        time.sleep(settings['update_interval'])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
