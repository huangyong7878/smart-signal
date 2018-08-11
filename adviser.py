import logging
from defaultstrategy import DefaultStrategy
from strategy002 import Strategy002
from exchange import ExchangeInterface

logger = logging.getLogger(__name__)
class Adviser:
    '''
    this class will eval current strategy to test if there is a buy or sell signal
    '''
    strategies = {"002":Strategy002(),"default":DefaultStrategy()}
    def __init__(self,config:dict,exchange:ExchangeInterface):
        if config.strategy ==None:
            self.strategy = Adviser.strategies['default']
        else:
            self.strategy = Adviser.strategies[config.strategy['name']]
        self.config = config
        self.exchange =exchange


    def work(self):
        interval = self.strategy.ticker_interval
        for _pair in self.config.settings['market_pairs']:
            thistory = self.exchange.get_candle_history(_pair, interval)
            (buy, sell) = self.strategy.get_signal(_pair, interval, thistory)
            if(buy):
                logger.info("should buy now")
            if sell:
                logger.info("should sell now");

        return False

