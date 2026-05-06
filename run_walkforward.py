# libraries 
import numpy as np
from collections import defaultdict

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
from data.Processed.data_handler import load_market_data
from research.regime import RegimeDetector

# Walkforward
from research.walk_forward import WalkForwardOptimizer

# Metrics
from metrics.performance import window_sharpes
from metrics.results_tracker import ResultsTracker
from metrics.performance import max_drawdown_curve

#Benchmark
from benchmark.buy_hold import BuyAndHoldBenchmark

#Utils
from utils.visualization import plot_switching_performance

#config
from config.config import INITIAL_CASH, TRANSACTION_COST

#Load data and initialize components
# Symbol = input("Ticker:")
# Start_date = input("Start Date (YYYY-MM-DD):")
# End_date = input("End Date (YYYY-MM-DD):")

Symbol = "META"
Start_date = "2014-01-01"
End_date = "2024-01-01"

csv_asset = load_market_data(Symbol,Start_date, End_date)
data_handler = DataHandler(f"data/raw/{Symbol}.csv")
data = data_handler.get_data()

# Strategy Grid (walk_forward)
strategies_grid = {
    "ma":[
        {"short":5, "long":20},
        {"short":20, "long":50},
    ],
    "zscore":[
        {"window":20},
    ]
}

# Base Strategy
base_strategies = {
    "ma":MovingAverageStrategy,
    "zscore" :ZscoreStrategy 
}

#Regime detector
regime_detector = RegimeDetector()

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
    portfolio_factory=lambda: Portfolio(INITIAL_CASH),
)


# Run Walk_forward
results = optimizer.run(base_strategies,regime_detector=regime_detector)

#plotting evaluations
for strat in base_strategies.keys():

    print(f"\n=== {strat.upper()} RESULTS ===")



    sharpes = window_sharpes(results,strat)
    sharpes = [float(x) for x in sharpes]

    print("Window Sharpe:", sharpes)
plot_switching_performance(results)

# Metrics
regime_returns = defaultdict(list)
regime_equity = defaultdict(list)

for res in results:
    regime = res["regime"]
    equity = np.array(res["equity"],dtype=float)
    if len(equity) >1:
        returns = np.diff(equity) / (equity[:-1]+1e-9)
        regime_returns[regime].extend(returns)
        regime_equity[regime].extend(equity)

# Evaluation
print("\n=== REGIME PERFORMANCE (SWITCHING MODEL) ===")
for r in ["trend", "chop", "high_vol"]:
    rets = regime_returns[r]
    eq = regime_equity[r]

    if len(rets) > 0:
        # Annualized Sharpe (assuming daily data)
        sharpe = (np.mean(rets) / (np.std(rets) + 1e-9)) * np.sqrt(252)
    else:
        sharpe = 0.0

    if len(eq) > 0:
        dd = max_drawdown_curve(eq)
    else:
        dd = 0.0

    print(f"Regime: {r:10} | Sharpe: {sharpe:6.3f} | MaxDD: {dd:6.3f}")
        

