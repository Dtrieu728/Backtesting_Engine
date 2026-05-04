from config.config import TRANSACTION_COST
import numpy as np

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
        turnover_curve = {name:[] for name in self.strategies.keys()}
        max_order = 1e3
        
        for i in range(len(self.data)):
            current_data = self.data.iloc[:i+1]
            price = current_data['close'].iloc[-1]
            
            for name,strategy in self.strategies.items():
        
                signal=strategy.generate_signal(current_data)
                portfolio = self.portfolios[name]
                order = self.signal_handler.generate_order(
                    signal, 
                    portfolio,
                    price
                )
                
                #avoids micro orders that can cause issues in execution and performance metrics
                if abs(order) < 1e-6:
                    order = 0.0
                    
                order = np.clip(order,-max_order,max_order)
                old_pos = portfolio.position
                
                if not np.isfinite(price):
                    continue
                if not np.isfinite(order):
                    order = 0.0
                
                
                # Transaction cost
                cost = abs(order) * price * TRANSACTION_COST
                
                # Execute order
                fill_price = self.execution.execute_order(order, price)
                
                #update portfolio
                portfolio.update(order, fill_price, cost)
                
                new_pos = portfolio.position
                
            
                #Equity curve and turnover
                equity = portfolio.cash + portfolio.position * price
                if not np.isfinite(equity) or equity <= 0:
                    return 0.0
                
                turnover = abs(new_pos - old_pos)*price /equity
                
                turnover_curve[name].append(turnover)
                equity_curve[name].append(equity)
                # print(name, signal, portfolio.position)
                # print(name, portfolio.cash, portfolio.position)

            
        return equity_curve, turnover_curve
    