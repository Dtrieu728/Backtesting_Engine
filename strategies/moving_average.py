from .base_strategy import BaseStrategy
import numpy as np

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, params):
        self.short = params["short"]
        self.long = params["long"]

    def generate_signal(self, data):
        close = data["close"]

        if len(close) < self.long:
            return 0.0

        short_ma = close.rolling(self.short).mean().iloc[-1]
        long_ma = close.rolling(self.long).mean().iloc[-1]

        if np.isnan(short_ma) or np.isnan(long_ma):
            return 0.0

        # normalized signal 
        signal = (short_ma - long_ma) / (long_ma + 1e-9)

        return np.tanh(signal * 10)  # bounded exposure