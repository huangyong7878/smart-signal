from indicators.indicator import Indicator
from exchangedata import ExchangeDataUtil
from talib import abstract
from datetime import datetime

class MACD(Indicator):
    def analyze(self, data, key=None, hot_thresh=None, cold_thresh=None):
        dataframe = ExchangeDataUtil.convert_to_dataframe(data)
        macd_values = abstract.MACD(dataframe).iloc[:]
        macd_values.dropna(how='all', inplace=True)
        signal = ['macdsignal']
        if macd_values[signal[0]].shape[0]:
            macd_values['is_hot'] = macd_values[signal[0]] > hot_thresh
            macd_values['is_cold'] = macd_values[signal[0]] < cold_thresh

        return macd_values
