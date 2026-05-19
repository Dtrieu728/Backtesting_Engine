import datetime
import numpy as np 
import pandas as pd

from abc import ABCMeta, abstractmethod
from core.eventDriven import SignalEvent

class Strategy(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    
    def calculate_signals(self,event):
        """Provides the mechanisms to calculate the list of signals

        Args:
            event (_type_): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError("Should implement calculate_signals()")

class BuyAndHoldStrategy(Strategy):
    def __init__(self,bars,events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.bought = self._calculate_initial_bought()
        
    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought
    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG', 1)
                        self.events.put(signal)
                        self.bought[s] = True