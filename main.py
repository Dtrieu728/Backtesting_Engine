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

tracker = ResultsTracker()
data_handler = DataHandler("data/raw/AAPL.csv")
data = data_handler.get_data()

# Initialize strategies
strategies = {"MA_20_50": MovingAverageStrategy(20, 50),
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
equity_curve = engine.run()
#add results to tracker
tracker.add_strategy_results(name="MA_20_50", equity_curve=equity_curve["MA_20_50"])
tracker.add_strategy_results(name="RSI", equity_curve=equity_curve["RSI"])
tracker.add_strategy_results(name="Zscore", equity_curve=equity_curve["Zscore"])



returns = compute_returns(equity_curve)
plot_equity_curves(tracker.get_all())
performance_summary(tracker.get_all())

print("Sharpe:", sharpe_ratio(returns))
print("Max Drawdown:", max_drawdown(equity_curve))