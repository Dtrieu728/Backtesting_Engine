from .base_strategy import BaseStrategy
import numpy as np
class RSIStrategy(BaseStrategy):
    def __init__(self, params):
        self.window = params["window"]
        
    def generate_signal(self, data):

        delta = data["close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1/self.window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.window, adjust=False).mean()

        rs = avg_gain / (avg_loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))

        latest_rsi = rsi.iloc[-1]

        if np.isnan(latest_rsi):
            return 0

        if latest_rsi < 30:
            return 1
        elif latest_rsi > 70:
            return -1
        else:
            return 0