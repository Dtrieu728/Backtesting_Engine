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
from utils.visualization import plot_switching_performance,plot_equity_with_regimes,plot_portfolio_value

#config
from config.config import INITIAL_CASH, TRANSACTION_COST

#Load data and initialize components
Symbol = input("Ticker:")
# Start_date = input("Start Date (YYYY-MM-DD):")
# End_date = input("End Date (YYYY-MM-DD):")

# Symbol = "MSFT"
Start_date = "2014-01-01"
End_date = "2024-01-01"

csv_asset = load_market_data(Symbol,Start_date, End_date)
data_handler = DataHandler(f"data/raw/{Symbol}.csv")
data = data_handler.get_data()

# Strategy Grid (walk_forward)
strategies_grid = {
    "ma":[
        {"short":5, "long":20},
        {"short":10, "long":30},
        {"short":20, "long":50}
    ],
    "zscore":[
        {"window":10},
        {"window":20},
        {"window":40}
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
    
#Benchmark (Buy and Hold)
bh = BuyAndHoldBenchmark(Symbol)
bh_equity = bh.run(data)

# plot_switching_performance(results,bh_equity)
plot_equity_with_regimes(results)
# plot_portfolio_value(results)




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
print("\n" + "="*55)
print(f"{'REGIME':<12} | {'SHARPE':<8} | {'MAX DD':<8} | {'TRADES':<6}")
print("-"*55)

for r in ["trend", "chop", "high_vol"]:
    rets = regime_returns.get(r, [])
    eq = regime_equity.get(r, [])
    
    # Calculate Sharpe
    sharpe = 0.0
    if len(rets) > 1: # Need at least 2 points for Std Dev
        std = np.std(rets)
        if std > 0:
            sharpe = (np.mean(rets) / std) * np.sqrt(252)

    # Calculate Max Drawdown
    dd = 0.0
    if len(eq) > 1:
        rolling_max = np.maximum.accumulate(eq)
        drawdowns = (eq - rolling_max) / rolling_max
        dd = np.min(drawdowns)

    print(f"{r.capitalize():<12} | {sharpe:8.3f} | {dd:8.3f} | {len(rets):<6}")
print("="*55)
        

