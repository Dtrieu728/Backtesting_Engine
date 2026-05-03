class SignalHandler:
    def generate_order(self, signal):
        if isinstance(signal, str):
            signal = signal.strip().upper()
            if signal == "BUY":
                return 1.0
            elif signal == "SELL":
                return -1.0
            else:
                return 0.0

        try:
            return float(signal)
        except (TypeError, ValueError):
            return 0.0
    