class ExecutionHandler:
    def __init__(self, slippage=0.0005, commission=0.0005):
        self.slippage = slippage
        self.commission = commission

    def execute_order(self, order, price):
        if order == 0:
            return price, 0.0

        # slippage-adjusted fill
        if order > 0:
            fill_price = price * (1 + self.slippage)
        else:
            fill_price = price * (1 - self.slippage)

        # commission in dollars
        cost = abs(order) * fill_price * self.commission

        return fill_price, cost