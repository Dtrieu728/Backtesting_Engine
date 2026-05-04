import numpy as np
class SignalHandler:
    def __init__(self, fraction=0.9):
        self.fraction = fraction

    def generate_order(self, signal, portfolio, price):
        # --- normalize signal FIRST ---
        max_shares = 1e4  # cap to avoid extreme orders
        if isinstance(signal, str):
            signal = signal.strip().upper()
            if signal == "BUY":
                signal = 1
            elif signal == "SELL":
                signal = -1
            else:
                signal = 0

        try:
            signal = float(signal)
        except (TypeError, ValueError):
            signal = 0.0

        # --- compute current equity ---
        equity = portfolio.cash + portfolio.position * price

        # --- target position based on capital ---
        target_value = signal * equity * self.fraction
        target_position = target_value / price
        target_position = np.clip(target_position, -max_shares, max_shares)

        # --- order = change needed ---
        order = target_position - portfolio.position

        return order