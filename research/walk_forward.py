# research/walk_forward.py
import numpy as np

class WalkForwardOptimizer:
    def __init__(self, engine_class, strategies, data,
                 train_window, test_window, step):
        self.engine_class = engine_class
        self.strategies = strategies
        self.data = data
        self.train_window = train_window
        self.test_window = test_window
        self.step = step

    def split(self):
        for start in range(0, len(self.data) - self.train_window - self.test_window, self.step):
            train = self.data.iloc[start:start+self.train_window]
            test = self.data.iloc[start+self.train_window:start+self.train_window+self.test_window]
            yield train, test
            
    def optimize(self, train_data,base_strategies):
        best_params = {}
        
        for name, strategy_class in base_strategies.items():
            best_sharpe = -np.inf
            best_params = None
            
            for params in self.strategies_grid[name]:
                engine = self.engine_class(
                    data = train_data,
                    strategies ={name:strategy},
                    signal_handler=...,
                    execution =...,
                    portfolio_factory = ...
                )
                
                equity,_ = engine.run()
                sharpe = compute_sharpe(equity[name])
                
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_param = params
                    
            best_param[name] = best_param
        return best_params
    
    def test(self, test_data,best_params,base_strategies):
        strategies = {
            name:base_strategies[name](param=best_params[name])
            for name in base_strategies
        }
        
        engine = self.engine_class(
                    data = train_data,
                    strategies ={name:strategy},
                    signal_handler=...,
                    execution =...,
                    portfolio_factory = ...
                )
        return engine.run()
    
    
    def run(self,base_strategies):
        results = []
        
        for train, test in self.split():
            best_params = self.optimize(train,base_strategies)
            
            equity, turnover = self.test(test,best_params,base_strategies)
            
            results.append({
                "equity":equity,
                "turnover":turnover,
                "params": best_params
            })
        
        return results