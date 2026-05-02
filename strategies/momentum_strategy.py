class RSIStrategy:
    def __init__(self, window=14):
        self.window = window
        
    def generate_signal(self, data):
        delta = data['close'].diff()
        
        gain = delta.clip(lower=0).rolling(self.window).mean()
        loss = -delta.clip(upper=0).rolling(self.window).mean()
        
        rs = gain/loss
        rsi = 100 - (100/(1+rs))
        
        signal = (rsi <30).astype(int) -(rsi>70).astype(int)
        
        return signal