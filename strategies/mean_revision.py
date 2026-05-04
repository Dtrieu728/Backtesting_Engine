from .base_strategy import BaseStrategy
import numpy as np
class ZscoreStrategy(BaseStrategy):
    def __init__(self, window=20):
        self.window = window

    def generate_signal(self, data):
        price = data['close']
        
        mean =  price.rolling(self.window).mean().iloc[-1] 
        std = price.rolling(self.window).std().iloc[-1]
        
        
        if std == 0 or np.isnan(std):
            return 0
        
        z = (price.iloc[-1] - mean) / (std + 1e-9)
        
        signal = -z
        
        signal = np.clip(signal, -1, 1)
        
        return signal