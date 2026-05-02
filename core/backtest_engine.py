class BacktestEngine:
    def __init__(self,data,strategies,signal_handler, execution,portfolio_factory):
        self.data =data
        self.strategies = strategies
        self.signal_handler = signal_handler
        self.execution = execution
        self.portfolio_factory = portfolio_factory
        
        self.portfolios ={
            name: portfolio_factory()
            for name in strategies.keys()
        }
        
    def run(self):
        equity_curve = {name:[] for name in self.strategies.keys()}
        
        for i in range(len(self.data)):
            current_data = self.data.iloc[:i+1]
            price = current_data['close'].iloc[-1]
            
            for name,strategy in self.strategies.items():
        
                signal_series =strategy.generate_signal(current_data)
                signal = signal_series.iloc[-1]
            
                order = self.signal_handler.generate_order(signal)
                fill_price = self.execution.execute_order(order,price)
            
                #update portfolio 
                portfolio =self.portfolios[name]
                portfolio.update(order,fill_price)
            
                #Equity curve
                equity = portfolio.get_equity(price)
                equity_curve[name].append(equity)
            
            
        return equity_curve
    