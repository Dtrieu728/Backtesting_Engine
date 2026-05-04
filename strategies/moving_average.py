from .base_strategy import BaseStrategy
import numpy as np

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, params):
        self.short_window = params["short"]
        self.long_window = params["long"]

    def generate_signal(self, data):
        if len(data) < self.long_window:
            return 0.0

        prices = data['close']

        short_ma = prices.rolling(self.short_window).mean().iloc[-1]
        long_ma = prices.rolling(self.long_window).mean().iloc[-1]

        if np.isnan(short_ma) or np.isnan(long_ma) or long_ma == 0:
            return 0.0

        # normalize DIFFERENCE by volatility proxy
        returns = prices.pct_change().dropna()
        vol = returns.std()

        if vol == 0 or np.isnan(vol):
            return 0.0

        signal = (short_ma - long_ma) / (long_ma * vol)

        # squash into stable range [-1, 1]
        signal = np.tanh(signal)

        return float(signal)