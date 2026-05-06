import numpy as np
class RegimeDetector:
    def __init__(self, vol_window=20):
        self.vol_window = vol_window

    def detect(self, data):
        if len(data) < self.vol_window + 1:
            return "chop"

        close = data["close"]
        returns = close.pct_change()

        # Volatility
        vol = returns.rolling(self.vol_window).std().iloc[-1]
        avg_abs_ret = returns.abs().rolling(self.vol_window).mean().iloc[-1]
        
        # Avoid division by zero and check for NaNs
        if np.isnan(vol) or avg_abs_ret < 1e-9:
            return "chop"
            
        vol_norm = vol / avg_abs_ret
        trend_strength = close.pct_change(self.vol_window).iloc[-1]

        # Logic
        if abs(trend_strength) > 0.02: 
            return "trend"
        
        if vol_norm > 2.0:
            return "high_vol"

        return "chop"