from config.config import INITIAL_CASH
from research.regime import RegimeDetector
import numpy as np

REGIME_MAP = {
    "trend": ["ma"],
    "chop": ["rsi", "zscore"],
    "high_vol": []
}

class BacktestEngine:
    def __init__(self,data,strategies,signal_handler, execution,portfolio_factory,regime_detector=None):
        self.data =data
        self.strategies = strategies
        self.signal_handler = signal_handler
        self.execution = execution
        self.portfolio_factory = portfolio_factory
        
        self.portfolios ={
            name: portfolio_factory()
            for name in strategies.keys()
        }
        self.regime_detector = regime_detector
        
    def run(self):

        equity_curve = {name: [] for name in self.strategies}
        turnover_curve = {name: [] for name in self.strategies}

        for i in range(len(self.data)):

            current_data = self.data.iloc[:i+1]
            price = current_data["close"].iloc[-1]

            if not np.isfinite(price):
                continue

            regime = None
            if self.regime_detector:
                regime = self.regime_detector.detect(current_data)
                if isinstance(regime, str):
                    regime = regime.lower().strip()

            for name, strategy in self.strategies.items():

                portfolio = self.portfolios[name]

                allowed = REGIME_MAP.get(regime, list(self.strategies.keys()))

                if name in allowed:
                    signal = strategy.generate_signal(current_data)
                else:
                    signal = 0

                order = self.signal_handler.generate_order(
                    signal, portfolio, price, current_data
                )

                if not np.isfinite(order):
                    order = 0.0

                max_position = 0.8 * (portfolio.cash + portfolio.position * price) / price
                target_position = np.clip(portfolio.position + order,
                                          -max_position,
                                          max_position)

                order = target_position - portfolio.position

                fill_price, cost_exec = self.execution.execute_order(order, price)

                portfolio.update(order, fill_price, cost_exec)

                equity = portfolio.cash + portfolio.position * price

                turnover = abs(order) * price / (equity + 1e-9)

                equity_curve[name].append(equity)
                turnover_curve[name].append(turnover)

        return equity_curve, turnover_curve