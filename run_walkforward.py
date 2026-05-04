# Strategies
from strategies.moving_average import MovingAverageStrategy
from strategies.momentum_strategy import RSIStrategy
from strategies.mean_revision import ZscoreStrategy

# Engine
from core.backtest_engine import BacktestEngine
from portfolio.portfolio import Portfolio
from signals.signal_handler import SignalHandler
from execution.execution_handler import ExecutionHandler
from data.Processed.data_handler import DataHandler
from research.regime import RegimeDetector

# Walkforward
from research.walk_forward import WalkForwardOptimizer

# Metrics
from metrics.performance import window_sharpes
from metrics.results_tracker import ResultsTracker

#Benchmark
from benchmark.buy_hold import BuyAndHoldBenchmark

#Utils
from utils.visualization import plot_equity, plot_turnover

#config
from config.config import INITIAL_CASH, TRANSACTION_COST

#Load data and initialize components

data_handler = DataHandler("data/raw/AAPL.csv")
data = data_handler.get_data()

# Strategy Grid (walk_forward)
strategies_grid = {
    "ma":[
        {"short":5, "long":20},
        {"short":10, "long":50},
        {"short":20, "long":100}
    ]
}

# Base Strategy
base_strategies = {
    "ma": MovingAverageStrategy
}

#Optimizer
optimizer = WalkForwardOptimizer(
    engine_class= BacktestEngine,
    strategies_grid= strategies_grid,
    data= data,
    train_window=500,
    test_window=100,
    step=100,
    signal_handler= SignalHandler(),
    execution = ExecutionHandler(),
    portfolio_factory=lambda: Portfolio(INITIAL_CASH)
)

#Regime detector
regime_detector = RegimeDetector()



# Run Walk_forward
strategy_name = "ma"
results = optimizer.run(base_strategies,regime_detector=regime_detector)
plot_equity(results,strategy_name)
plot_turnover(results,strategy_name)

sharpes = window_sharpes(results,strategy_name)
sharpes = [float(x)for x in sharpes]
print("Window Sharpe:" , sharpes)
# print(results)


