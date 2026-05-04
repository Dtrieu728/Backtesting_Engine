# research/walk_forward.py
import numpy as np

class WalkForwardOptimizer:
    def __init__(self, engine_class, strategies_grid, data,
                 train_window, test_window, step,
                 signal_handler, execution, portfolio_factory):

        self.engine_class = engine_class
        self.strategies_grid = strategies_grid
        self.data = data

        self.train_window = train_window
        self.test_window = test_window
        self.step = step

        self.signal_handler = signal_handler
        self.execution = execution
        self.portfolio_factory = portfolio_factory

    def split(self):
        for start in range(0, len(self.data) - self.train_window - self.test_window, self.step):
            train = self.data.iloc[start:start+self.train_window]
            test = self.data.iloc[start+self.train_window:start+self.train_window+self.test_window]
            yield train, test
            
    def optimize(self, train_data, base_strategies):

        best_params = {}

        for name, strategy_class in base_strategies.items():

            best_sharpe = -np.inf
            best_param_for_strategy = None

            for params in self.strategies_grid[name]:

                strategy = strategy_class(params=params)

                engine = self.engine_class(
                    data=train_data,
                    strategies={name: strategy},
                    signal_handler=self.signal_handler,
                    execution=self.execution,
                    portfolio_factory=self.portfolio_factory
                    )

                equity, _ = engine.run()
                
                returns = np.diff(equity[name])/equity[name][:-1]
                sharpe =np.mean(returns)/ np.std(returns)

                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_param_for_strategy = params

            best_params[name] = best_param_for_strategy

        return best_params
    
    def test(self, test_data, best_params, base_strategies):

        strategies = {
            name: base_strategies[name](params=best_params[name])
            for name in base_strategies
        }

        engine = self.engine_class(
            data=test_data,
            strategies=strategies,
            signal_handler=self.signal_handler,
            execution=self.execution,
            portfolio_factory=self.portfolio_factory
        )

        return engine.run()
    
    
    def run(self, base_strategies):

        results = []

        for train, test in self.split():

            best_params = self.optimize(train, base_strategies)

            equity, turnover = self.test(test, best_params, base_strategies)

            results.append({
                "equity": equity,
                "turnover": turnover,
                "params": best_params
            })

        return results