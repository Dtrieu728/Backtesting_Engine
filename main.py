from data.Processed.data_handler import DataHandler
from strategies.moving_average import MovingAverageStrategy
from signals.signal_handler import SignalHandler
from execution.execution_handler import ExecutionHandler
from portfolio.portfolio import Portfolio
from core.backtest_engine import BacktestEngine
from metrics.performance import *

from config.config import *

data_handler = DataHandler("data/raw/AAPL.csv")
data = data_handler.get_data()

strategy = MovingAverageStrategy(SHORT_WINDOW, LONG_WINDOW)
signal_handler = SignalHandler()
execution = ExecutionHandler()
portfolio = Portfolio(INITIAL_CASH)

engine = BacktestEngine(data, strategy, signal_handler, execution, portfolio)
equity_curve = engine.run()

returns = compute_returns(equity_curve)

print("Sharpe:", sharpe_ratio(returns))
print("Max Drawdown:", max_drawdown(equity_curve))