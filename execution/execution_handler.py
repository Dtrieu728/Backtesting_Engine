class ExecutionHandler:
    def __init__(self,slippage=0.001,commission=0.001):
        self.slippage = slippage
        self.commission = commission
    def execute_order(self,order,price):
        if order == 'BUY':
            price = price * (1 + self.slippage)
        elif order == 'SELL':
            price = price * (1 - self.slippage)
        
        return price *(1+self.commission)