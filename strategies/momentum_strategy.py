import numpy as np
class RSIStrategy:
    def __init__(self, window=14):
        self.window = window
        
    def generate_signal(self, data):
        delta = data['close'].diff()
        
        gain = delta.clip(lower=0).rolling(self.window).mean()
        loss = -delta.clip(upper=0).rolling(self.window).mean()
        
        rs = gain/ (loss + 1e-9)
        rsi = 100 - (100/(1+rs))
        
        latest_rsi = rsi.iloc[-1]
        
        if np.isnan(latest_rsi):
            return 0
        
        if latest_rsi < 30:
            return 1
        elif latest_rsi > 70:
            return -1
        else:
            return 0