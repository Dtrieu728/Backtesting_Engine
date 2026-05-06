from .base_strategy import BaseStrategy
import numpy as np

class RSIStrategy(BaseStrategy):
    def __init__(self, params):
        self.window = params["window"]

    def generate_signal(self, data):

        delta = data["close"].diff()

        gain = (delta.where(delta>0,0)).rolling(self.window).mean()
        loss = (-delta.where(delta < 0,0)).rolling(self.window).mean()

        avg_gain = gain.ewm(alpha=1/self.window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.window, adjust=False).mean()

        rs = avg_gain / (avg_loss)
        rsi = 100 - (100 / (1 + rs))

        latest = rsi.iloc[-1]

        if np.isnan(latest):
            return 0

        # continuous signal 
        if latest < 50:
            signal = (50 - latest) / 20   
        else:
            signal = -(latest - 50) / 20  

        return np.clip(signal, -1, 1)