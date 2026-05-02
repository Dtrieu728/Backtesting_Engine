class Portfolio:
    def __init__(self,initial_cash):
        self.cash = initial_cash
        self.position= 0 
        self.history = []
        
    def update(self,order,price):
        if order == "BUY":
            self.position += 1
            self.cash-=price
        elif order == "SELL":
            self.position-=1 
            self.cash +=price
        
        self.history.append(self.cash + self.position * price)