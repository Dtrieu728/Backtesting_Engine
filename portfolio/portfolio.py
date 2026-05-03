class Portfolio:
    def __init__(self,initial_cash):
        self.cash = initial_cash
        self.position= 0 
        self.history = []
        
    def update(self,order,exec_price):
        self.cash -= order * exec_price
        self.position += order
    
    def get_equity(self,price):
        return self.cash + self.position * price
    
    def record(self,price):
        equity = self.get_equity(price)
        self.history.append(equity)