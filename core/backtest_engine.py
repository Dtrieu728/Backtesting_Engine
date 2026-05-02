class BacktestEngine:
    def __init__(self,data,strategy,signal_handler, execution,portfolio):
        self.data =data
        self.strategy = strategy
        self.signal_handler = signal_handler
        self.execution = execution
        self.portfolio = portfolio
        
    def run(self):
        for i in range(len(self.data)):
            current_data = self.data.iloc[:i+1]
            price = current_data['close'].iloc[-1]
            
            signal_series = self.strategy.generate_signal(current_data)
            signal = signal_series.iloc[-1]
            
            order = self.signal_handler.generate_order(signal)
            fill_price = self.execution.execute_order(order,price)
            
            self.portfolio.update(order,fill_price)
            
        return self.portfolio.history