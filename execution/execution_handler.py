class ExecutionHandler:
    def __init__(self, slippage=0.0005, commission=0.0005, spread=0.0005):
        self.slippage = slippage
        self.commission = commission
        self.spread = spread

    def execute_order(self, order, price, volume=None):
        if order == 0:
            return price, 0.0

        # liquidity impact 
        impact = 0
        if volume is not None:
            impact = abs(order) / (volume + 1e-9)

        dynamic_slippage = self.slippage * (1 + impact)

        # bid-ask spread 
        if order > 0:
            fill_price = price * (1 + self.spread/2 + dynamic_slippage)
        else:
            fill_price = price * (1 - self.spread/2 - dynamic_slippage)

        # commission 
        cost = abs(order) * fill_price * self.commission

        return fill_price, cost