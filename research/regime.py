import numpy as np
class RegimeDetector:
    def __init__(self, vol_window=20, vol_threshold=0.01,
                 short_window=10, long_window=50):

        self.vol_window = vol_window
        self.vol_threshold = vol_threshold
        self.short_window = short_window
        self.long_window = long_window

    def detect(self, data):

        returns = data["close"].pct_change()

        # volatility
        vol = returns.rolling(self.vol_window).std().iloc[-1]

        # trend strength
        close = data["close"]

        short_ma = close.rolling(self.short_window).mean().iloc[-1]
        long_ma = close.rolling(self.long_window).mean().iloc[-1]

        trend_strength = abs(short_ma - long_ma) / close.iloc[-1]

        if np.isnan(trend_strength):
            return "low_vol"

        if trend_strength > 0.03:
            return "trend"

        return "chop"