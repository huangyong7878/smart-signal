from abc import ABC
from abc import ABC, abstractmethod
import pandas as pd
from pandas import DataFrame
from enum import Enum
import logging
from typing import List, Dict, Tuple
import arrow
import constants
from pandas import DataFrame, to_datetime


class SignalType(Enum):
    """
    Enum to distinguish between buy and sell signals
    """
    BUY = "buy"
    SELL = "sell"


logger = logging.getLogger(__name__)


class IStrategy(ABC):
    ticker_interval: str

    @abstractmethod
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pass

    @abstractmethod
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pass

    @abstractmethod
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pass

    def parse_ticker_dataframe(self, ticker: list) -> DataFrame:
        """
           Analyses the trend for the given ticker history
           :param ticker: See exchange.get_candle_history
           :return: DataFrame
           """
        cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        frame = DataFrame(ticker, columns=cols)
        # frame['datetime'] = frame.timestamp.apply(
        #     lambda x: pd.to_datetime(frame.fromtimestamp(x / 1000).strftime('%c'))
        # )

        frame['date'] = to_datetime(frame['date'],
                                    unit='ms',
                                    utc=True,
                                    infer_datetime_format=True)

        # group by index and aggregate results to eliminate duplicate ticks
        frame = frame.groupby(by='date', as_index=False, sort=True).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'max',
        })
        frame.drop(frame.tail(1).index, inplace=True)  # eliminate partial candle
        return frame

    def advise_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self.populate_indicators(dataframe, metadata)

    def advise_buy(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self.populate_buy_trend(dataframe, metadata)

    def advise_sell(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self.populate_sell_trend(dataframe, metadata)

    def analyze_ticker(self, ticker_history: List[Dict], metadata: dict) -> DataFrame:
        """
        Parses the given ticker history and returns a populated DataFrame
        add several TA indicators and buy signal to it
        :return DataFrame with ticker data and indicator data
        """
        dataframe = self.parse_ticker_dataframe(ticker_history)
        dataframe = self.advise_indicators(dataframe, metadata)
        dataframe = self.advise_buy(dataframe, metadata)
        dataframe = self.advise_sell(dataframe, metadata)
        return dataframe

    def get_signal(self, pair: str, interval: str, ticker_hist: List[Dict]) -> Tuple[bool, bool]:
        """
        Calculates current signal based several technical analysis indicators
        :param pair: pair in format ANT/BTC
        :param interval: Interval to use (in min)
        :return: (Buy, Sell) A bool-tuple indicating buy/sell signal
        """
        if not ticker_hist:
            logger.warning('Empty ticker history for pair %s', pair)
            return False, False

        try:
            dataframe = self.analyze_ticker(ticker_hist, {'pair': pair})
        except ValueError as error:
            logger.warning(
                'Unable to analyze ticker for pair %s: %s',
                pair,
                str(error)
            )
            return False, False
        except Exception as error:
            logger.exception(
                'Unexpected error when analyzing ticker for pair %s: %s',
                pair,
                str(error)
            )
            return False, False

        if dataframe.empty:
            logger.warning('Empty dataframe for pair %s', pair)
            return False, False

        latest = dataframe.iloc[-1]

        # Check if dataframe is out of date
        signal_date = arrow.get(latest['date'])
        interval_minutes = constants.TICKER_INTERVAL_MINUTES[interval]
        if signal_date < (arrow.utcnow().shift(minutes=-(interval_minutes * 2 + 5))):
            logger.warning(
                'Outdated history for pair %s. Last tick is %s minutes old',
                pair,
                (arrow.utcnow() - signal_date).seconds // 60
            )
            return False, False

        (buy, sell) = latest[SignalType.BUY.value] == 1, latest[SignalType.SELL.value] == 1
        logger.info(
            'trigger: %s (pair=%s) buy=%s sell=%s',
            latest['date'],
            pair,
            str(buy),
            str(sell)
        )
        return buy, sell
