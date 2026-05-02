class SignalHandler:
    def generate_order(self,signal):
        if signal == 1:
            return 'BUY'
        elif signal == -1:
            return 'SELL'
        else:
            return 'HOLD'
    