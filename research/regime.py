import numpy as np

class RegimeDetector:
    def __init__(self, vol_window=20):
        self.vol_window = vol_window

    def detect(self, data):

        close = data["close"]
        returns = close.pct_change()

        vol = returns.rolling(self.vol_window).std().iloc[-1]

        short_ma = close.rolling(10).mean().iloc[-1]
        long_ma = close.rolling(50).mean().iloc[-1]

        if np.isnan(vol):
            return "chop"

        trend_strength = (short_ma - long_ma) / (close.iloc[-1] + 1e-9)
        vol_norm = vol / (np.mean(returns.abs()) + 1e-9)

        if vol_norm > 2.0:
            return "high_vol"
        elif abs(trend_strength) > 0.015:
            return "trend"
        else:
            return "chop"