import numpy as np
class SignalHandler:
    def __init__(self, fraction=0.02, adjustment_speed=0.2):
        self.fraction = fraction
        self.adjustment_speed = adjustment_speed

    def generate_order(self, signal, portfolio, price, data=None):

        # normalize signal 
        try:
            signal = float(signal)
        except:
            return 0.0

        signal = np.clip(signal, -1, 1)

        equity = portfolio.cash + portfolio.position * price
        if equity <= 0:
            return 0.0

        #volatility 
        if data is not None and len(data) > 20:
            returns = data['close'].pct_change()
            vol = returns.rolling(20).std().iloc[-1]
        else:
            vol = 0.02

        vol = max(vol, 0.01)

        # position sizing
        target_value = signal * equity * self.fraction / vol
        target_position = target_value / price

        # cap exposure 
        max_position_value = 0.5 * equity
        target_position = np.clip(
            target_position,
            -max_position_value / price,
            max_position_value / price
        )

        # smooth trading 
        order = (target_position - portfolio.position) * self.adjustment_speed

        # filter small trades 
        if abs(order) * price < 50:
            return 0.0

        return order