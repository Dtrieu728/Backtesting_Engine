from .base_strategy import BaseStrategy
import numpy as np

class ZscoreStrategy(BaseStrategy):
    def __init__(self, params):
        self.window = params["window"]

    def generate_signal(self, data):
        price = data["close"]

        if len(price) < self.window:
            return 0.0

        mean = price.rolling(self.window).mean().iloc[-1]
        std = price.rolling(self.window).std().iloc[-1]

        if np.isnan(std) or std == 0:
            return 0.0

        z = (price.iloc[-1] - mean) / (std + 1e-9)

        # mean reversion signal
        signal = -z / (1 + abs(z))

        return signal