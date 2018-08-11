# coding=utf-8
import yaml
import ccxt

class Config():
    """
    settings : logging...timeinterval ..etc

    information:
    indicators
    exchange:

    """
    def __init__(self,cf="config.yml"):
        """

        :param cf: configuration file
        """
        with open(cf,'r') as config_file:
            config = yaml.load(config_file)


        if 'settings' in config:
            self.settings={**config['settings']}

        if 'exchanges' in config:
            self.exchanges = {**config['exchanges']}

        if 'strategy' in config:
            self.strategy ={**config['strategy']}

        for exchange in ccxt.exchanges:
            if exchange not in self.exchanges:
                self.exchanges[exchange] = {
                    'required': {
                        'enabled': False
                    }
                }