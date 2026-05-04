import numpy as np

class SignalHandler:
    def __init__(self, fraction=0.2, max_shares=1e4):
        self.fraction = fraction
        self.max_shares = max_shares

    def generate_order(self, signal, portfolio, price):

        # 1. Normalize signal
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

        if not np.isfinite(signal):
            signal = 0.0

        
        # 2. Compute equity safely
        
        equity = portfolio.cash + portfolio.position * price

        if not np.isfinite(equity) or equity <= 0:
            return 0.0

        # 3. Volatility estimate (simple proxy)
        # fallback if no volatility tracking yet
        vol_proxy = abs(portfolio.position * price) / (equity + 1e-9)
        vol_proxy = max(vol_proxy, 0.05)  # prevent division blowups

        
        # 4. Risk-scaled position sizing
        risk_scaled_equity = equity * self.fraction / vol_proxy

        target_value = signal * risk_scaled_equity
        target_position = target_value / price

        # 5. Hard caps (safety layer)
        target_position = np.clip(
            target_position,
            -self.max_shares,
            self.max_shares
        )

        # 6. Generate order
        order = target_position - portfolio.position

        # 7. Final safety clamp
        if not np.isfinite(order):
            return 0.0

        return order