import numpy as np
class Portfolio:
    def __init__(self,initial_cash):
        self.cash = initial_cash
        self.position= 0 
        self.history = []
        
    def update(self,order,exec_price,cost):
        if not np.isfinite(order) or not np.isfinite(exec_price):
            return
        trade_value = order * exec_price
        if not np.isfinite(trade_value):
            return
        
        self.cash -= trade_value
        self.cash -= cost
        self.position += order
    
    def get_equity(self,price):
        return self.cash + self.position * price
    
    def record(self,price):
        equity = self.get_equity(price)
        self.history.append(equity)