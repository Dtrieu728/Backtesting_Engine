import numpy as np
class RegimeDetector:
    def __init__(self, vol_window=20,vol_threshold = 1.25):
        self.vol_window = vol_window
        self.vol_threshold = vol_threshold

    def detect(self, data):
        if len(data) < self.vol_window + 1:
            return "chop"

        close = data["close"]
        returns = close.pct_change()

        # Volatility
        current_vol = returns.tail(self.vol_window).std()
        hist_vol = returns.tail(60).std()
        
        if current_vol > (hist_vol*self.vol_threshold):
            return "high_vol"
            
        trend_strength = close.pct_change(self.vol_window).iloc[-1]

        # Logic
        if abs(trend_strength) > 0.05: 
            return "trend"

        return "chop"