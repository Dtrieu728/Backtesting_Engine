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
        strategy_scores = {}


        for name, strategy_class in base_strategies.items():

            print(f"\n Optimizing strategy: {name}")

            best_sharpe = -np.inf
            best_params = None

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

                returns = np.diff(equity[name]) / (np.array(equity[name][:-1]) + 1e-8)

                sharpe = sharpe = (np.mean(returns) / (np.std(returns) + 1e-9)) * np.sqrt(252)

                print(f"   Params: {params} → Sharpe: {sharpe:.4f}")

                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params= params

            print(f"Best Params: {best_params}, Sharpe: {best_sharpe:.4f}")

            strategy_scores[name] = (best_sharpe, best_params)

        return strategy_scores

    def test(self, test_data, strategy_scores, base_strategies):
        equity_all = {}
        turnover_all = {}

        for name, (_, params) in strategy_scores.items():
            strategy = base_strategies[name](params=params)

            engine = self.engine_class(
                data=test_data,
                strategies={name: strategy},
                signal_handler=self.signal_handler,
                execution=self.execution,
                portfolio_factory=self.portfolio_factory
            )

            equity, turnover = engine.run()

            equity_all[name] = equity[name]
            turnover_all[name] = turnover[name]

        return equity_all, turnover_all

    def run(self, base_strategies, regime_detector=None):
        results = []

        for i, (train, test) in enumerate(self.split()):
            best_params = self.optimize(train, base_strategies)
            equity, turnover = self.test(test, best_params, base_strategies)

            regime = regime_detector.detect(test) if regime_detector else None

            results.append({
                "equity": equity,
                "turnover": turnover,
                "params": best_params,
                "regime": regime
            })

        return results