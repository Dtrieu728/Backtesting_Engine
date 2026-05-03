import numpy as np

class BuyAndHoldBenchmark:
    def __init__(self, symbol):
        self.symbol = symbol
        
    def run(self, data):
        price = data['close'].values
        return price / price[0]