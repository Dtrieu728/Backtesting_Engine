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
        
        for i in range(len(self.data)):
            current_data = self.data.iloc[:i+1]
            price = current_data['close'].iloc[-1]
            
            for name,strategy in self.strategies.items():
        
                signal=strategy.generate_signal(current_data)
                
                portfolio = self.portfolios[name]
                old_pos = portfolio.position
    
                order = signal
                
                # Execute order
                exec_price = price + TRANSACTION_COST * price * np.sign(order)
                
                #update portfolio 
                portfolio.update(order, exec_price)
                
                new_pos = portfolio.position
                
                # Track turnover
                turnover = abs(new_pos- old_pos)
                turnover_curve[name].append(turnover)
            
                #Equity curve
                equity = portfolio.cash + portfolio.position * price
                equity_curve[name].append(equity)
                # print(name, signal, portfolio.position)
                # print(name, portfolio.cash, portfolio.position)
                
            
        return equity_curve, turnover_curve
    