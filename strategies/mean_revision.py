class ZscoreStrategy:
    def __init__(self, window=20):
        self.window = window

    def generate_signal(self, data):
        mean = data['close'].rolling(self.window).mean()
        std = data['close'].rolling(self.window).std()
        
        z = (data['close'] - mean) / std
        
        signal = (-1 * (z>2).astype(int)) + (1 * (z<-2).astype(int))
        return signal
    