import numpy as np
from config.config import INITIAL_CASH

REGIME_MAP = {
    "trend": "ma",
    "chop": "zscore",
    "high_vol": "ma"   
}


class BacktestEngine:
    def __init__(self, data, strategies, signal_handler, execution, portfolio_factory, regime_detector=None):
        self.data = data
        self.strategies = strategies
        self.signal_handler = signal_handler
        self.execution = execution
        self.portfolio = portfolio_factory()  
        self.regime_detector = regime_detector
        self.prev_regime = None
        self.regime_buffer = []
        self.buffer_size = 5

    def run(self):

        equity_curve = []
        turnover_curve = []
        
        is_single_strat = len(self.strategies) == 1
        single_strat_name = list(self.strategies.keys())[0] if is_single_strat else None

        for i in range(len(self.data)):

            current_data = self.data.iloc[:i+1]
            price = current_data["close"].iloc[-1]

            if not np.isfinite(price):
                continue
            


            #Detect regime
            if self.regime_detector and not is_single_strat:
                raw_regime = self.regime_detector.detect(current_data)
            else:
                raw_regime = single_strat_name if is_single_strat else "chop"
            self.regime_buffer.append(raw_regime)
            
            if len(self.regime_buffer) > self.buffer_size:
                self.regime_buffer.pop(0)
                
            if all(r==self.regime_buffer[0] for r in self.regime_buffer):
                confirmed_regime = self.regime_buffer[0]
            else:
                confirmed_regime = self.prev_regime if self.prev_regime else raw_regime
                
            if confirmed_regime != self.prev_regime and self.prev_regime is not None:
                order = -self.portfolio.position
                if order != 0:
                    fill_price, cost_exec = self.execution.execute_order(order,price)
                    self.portfolio.update(order,fill_price,cost_exec)
                    
            self.prev_regime = confirmed_regime

            #Select strategy
            if is_single_strat:
                strategy = self.strategies[single_strat_name]
            else:
                strategy_name = REGIME_MAP.get(confirmed_regime,"zscore")
                strategy = self.strategies.get(strategy_name,self.strategies.get("zscore"))
                
            if not strategy:
                raise ValueError (f"No strategy found for regime {regime} and no default available")

            signal = strategy.generate_signal(current_data)

            #Volatility-based sizing
            # returns = current_data["close"].pct_change()
            # vol = returns.rolling(20).std().iloc[-1]

            # target_vol = 0.02  # risk target
            # vol_scalar = target_vol / (vol + 1e-9)

            # equity = self.portfolio.cash + self.portfolio.position * price
            # max_position = vol_scalar * equity / price

            #Signal to order
            order = self.signal_handler.generate_order(
                signal, self.portfolio, price, current_data
            )

            if not np.isfinite(order):
                order = 0.0

            # target_position = np.clip(
            #     self.portfolio.position + order,
            #     -max_position,
            #     max_position
            # )

            # order = target_position - self.portfolio.position

            #Execution
            fill_price, cost_exec = self.execution.execute_order(order, price)
            self.portfolio.update(order, fill_price, cost_exec)


            #Metrics
            equity = self.portfolio.cash + self.portfolio.position * price
            turnover = abs(order) * price / (equity + 1e-9)

            equity_curve.append(equity)
            turnover_curve.append(turnover)

        return equity_curve, turnover_curve