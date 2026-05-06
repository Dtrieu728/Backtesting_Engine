import numpy as np
class RegimeDetector:
    def __init__(self, vol_window=20):
        self.vol_window = vol_window

    def detect(self, data):
        close = data["close"]
        returns = close.pct_change()

        # Volatility
        vol = returns.rolling(self.vol_window).std().iloc[-1]
        avg_abs_ret = returns.abs().rolling(self.vol_window).mean().iloc[-1]
        vol_norm = vol / (avg_abs_ret + 1e-9)

        # Trend (momentum-based, more robust)
        trend_strength = close.pct_change(20).iloc[-1]

        if np.isnan(vol) or np.isnan(trend_strength):
            return "chop"

        # Regime logic
        if abs(trend_strength) > 0.02:
            if vol_norm > 1.5:
                return "trend_high_vol"
            else:
                return "trend"

        if vol_norm > 2.0:
            return "high_vol"

        return "chop"