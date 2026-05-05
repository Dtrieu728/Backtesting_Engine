from config.config import TRANSACTION_COST,INITIAL_CASH
from research.regime import RegimeDetector
import numpy as np

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
            price = current_data['close'].iloc[-1]

            if not np.isfinite(price):
                continue

            regime = self.regime_detector.detect(current_data) if self.regime_detector else None

            for name, strategy in self.strategies.items():
                portfolio = self.portfolios[name]

                signal = strategy.generate_signal(current_data)
                signal = np.clip(signal, -1, 1)

                # optional regime scaling
                risk_multiplier = {
                    "trend": 1.2,
                    "chop": 0.6,
                    "high_vol": 0.4
                }.get(regime, 1.0)

                signal *= risk_multiplier

                order = self.signal_handler.generate_order(signal, portfolio, price)

                if not np.isfinite(order):
                    order = 0.0

                order = np.clip(order, -1e3, 1e3)

                equity = portfolio.cash + portfolio.position * price
                max_position = (0.8 * equity) / price if price != 0 else 0

                target_position = np.clip(portfolio.position + order, -max_position, max_position)
                order = target_position - portfolio.position

                fill_price, cost = self.execution.execute_order(order, price)
                portfolio.update(order, fill_price, cost)

                equity = portfolio.cash + portfolio.position * price

                turnover = abs(order) * price / (equity + 1e-9)

                equity_curve[name].append(equity)
                turnover_curve[name].append(turnover)

        return equity_curve, turnover_curve
    