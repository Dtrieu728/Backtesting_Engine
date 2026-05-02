from .base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signal(self,data):
        short_ma = data['close'].rolling(self.short_window).mean()
        long_ma = data['close'].rolling(self.long_window).mean()
        
        signal = (short_ma > long_ma).astype(int)
        return signal