from data.Processed.data_handler import DataHandler
from strategies.moving_average import MovingAverageStrategy
from strategies.momentum_strategy import RSIStrategy
from strategies.mean_revision import ZscoreStrategy
from signals.signal_handler import SignalHandler
from execution.execution_handler import ExecutionHandler
from portfolio.portfolio import Portfolio
from core.backtest_engine import BacktestEngine
from metrics.performance import *
from metrics.results_tracker import ResultsTracker
from config.config import *
from utils.visualization import *
from benchmark.buy_hold import BuyAndHoldBenchmark
from research.walk_forward import WalkForwardOptimizer

# ----------- #
#Backtest engine



# Initialize strategies
strategies = {"MA_50_200": MovingAverageStrategy(50, 200),
              "RSI": RSIStrategy(window=14),
              "Zscore": ZscoreStrategy(window=20)
              }

signal_handler = SignalHandler()
execution = ExecutionHandler()

engine = BacktestEngine(
    data, 
    strategies, 
    signal_handler, 
    execution, 
    portfolio_factory=lambda: Portfolio(INITIAL_CASH)
    )

# Run backtest 
equity_curve, turnover_curve = engine.run()


#add results to tracker
for name in equity_curve:
    tracker.add_strategy_results(name, equity_curve[name])

#Benchmark (Buy and Hold)
bh = BuyAndHoldBenchmark("AAPL")
bh_equity = bh.run(data)

bh_returns = np.diff(bh_equity) / bh_equity[:-1]
bh_sharpe = sharpe_ratio({"BuyHold": bh_returns})



#Prepare data for visualization
def normalize_curve(curve):
    curve = np.asarray(curve)
    return curve / curve[0]


raw_data = tracker.get_all()

strategy_returns = compute_returns(raw_data)
strategy_sharpe = sharpe_ratio(strategy_returns)
strategy_dd = max_drawdown(raw_data)

avg_turnover = {
    name: np.mean(turnover) 
    for name, turnover in turnover_curve.items()
}


#Visualization
plot_data = {
    name: normalize_curve(curve) 
    for name, curve in raw_data.items()
}
plot_data["Buy & Hold"] = normalize_curve(bh_equity)

plot_equity_curves(plot_data)
performance_summary(raw_data)


#Print performance summary
print("Strategy Sharpe:", strategy_sharpe)
print("Strategy Drawdown:", strategy_dd)
print("Average Turnover:", avg_turnover)
print("Buy & Hold Sharpe:", bh_sharpe)
