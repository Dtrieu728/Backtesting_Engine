from .base_strategy import BaseStrategy
import numpy as np

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signal(self,data):
        if len(data) < self.long_window:
            return 0
        
        short_ma = data['close'].rolling(self.short_window).mean().iloc[-1]
        long_ma = data['close'].rolling(self.long_window).mean().iloc[-1]
        
        if np.isnan(short_ma) or np.isnan(long_ma):
            return 0
        
        if short_ma > long_ma:
            return 1
        elif short_ma < long_ma:
            return -1
        else:
            return 0