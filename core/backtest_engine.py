from config.config import TRANSACTION_COST,INITIAL_CASH
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
            
            if not np.isfinite(price):
                continue
            
            for name,strategy in self.strategies.items():
                portfolio = self.portfolios[name]
                
                signal = strategy.generate_signal(current_data)
                order = self.signal_handler.generate_order(
                    signal, 
                    portfolio,
                    price
                )
                if not np.isfinite(order):
                    order = 0.0
                order = np.clip(order,-1e3,1e3)
                
                target_position=portfolio.position + order
                equity = portfolio.cash + portfolio.position * price
                
        
                max_exposure = 0.3 * equity
                max_position = max_exposure / price if price != 0 else 0.0
                
                target_position = np.clip(target_position,-max_position,max_position)
                order = target_position - portfolio.position
                
                         
                # Transaction cost
                cost = abs(order) * price * TRANSACTION_COST
                
                # Execute order
                fill_price = self.execution.execute_order(order, price)
                
                
                #update portfolio
                portfolio.update(order,fill_price,cost)
                equity = portfolio.cash + portfolio.position * price
                equity = max(equity,1e-8)
                
                leverage = abs(portfolio.position * price) /equity
                if leverage >1.0:
                    scale = 1.0 /leverage
                    portfolio.position *= scale
                    
                #Equity curve and turnover
                new_equity = portfolio.cash + portfolio.position*price
                turnover = abs(order)*price /equity
                
                
                turnover_curve[name].append(turnover)
                equity_curve[name].append(equity)
                # print(name, signal, portfolio.position)
                # print(name, portfolio.cash, portfolio.position)

            
        return equity_curve, turnover_curve
    