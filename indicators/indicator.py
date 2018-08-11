import abc
from abc import ABC
class Indicator(ABC):
    @abc.abstractmethod
    def analyze(self,data,key,hot_thresh=None, cold_thresh=None):
        return None;
