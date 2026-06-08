import pandas as pd
import matplotlib.pyplot as plt
import math
from datetime import datetime
from matplotlib import style
from core.event import SignalEvent
from strategies.strategy import Strategy


class RSIMeanReversionStrategy(Strategy):
    def __init__(self,data,events, portfolio, period=14, threshold=30, version=1, verbose=False):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.period = period
        self.threshold = threshold
   
        self.name = 'RSI Mean Reversion'
        self.version = version
        self.verbose = verbose
        
        
        self.signals = self._setup_signals()
        self.bought = self._setup_initial_bought()
    
    def _setup_signals(self):
        signals = {}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date', 'Signal'])

        return signals
    
    
    def _setup_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought
    
    def compute_rsi(self, closes, period):
        if len(closes) < period + 1:
            return None
        
        delta = closes.diff()
        
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = avg_loss.replace(0, 1e-10)
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                # get all available data for this symbol
                data = self.data.get_latest_data(
                    symbol, N=len(self.data.latest_symbol_data[symbol])
                )
                if data is None or len(data) < self.period + 1:
                    continue

                df = pd.DataFrame(data, columns=['Symbol', 'Date', 'Close'])
                df.set_index('Date', inplace=True)

                rsi = self.compute_rsi(df['Close'], self.period)
                if rsi is None:
                    continue

                date  = data[-1][self.data.time_col]
                price = data[-1][self.data.price_col]

                if self.verbose:
                    print(f"[RSI] {symbol} {date} RSI={rsi:.2f}")

                # RSI < threshold → oversold → BUY
                if not self.bought[symbol] and rsi < self.threshold:
                    current_positions = self.portfolio.current_positions[symbol]
                    if current_positions < 0:
                        signal = SignalEvent(symbol, date, 'EXIT', math.fabs(current_positions))
                        self.events.put(signal)

                    quantity = math.floor(self.portfolio.current_holdings['cash'] / price)
                    if quantity > 0:
                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True

                        new_row = pd.DataFrame({'Signal': [quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat(
                            [self.signals[symbol], new_row], ignore_index=True
                        )
                        if self.verbose:
                            print(f"[RSI] BUY {symbol} @ {price} RSI={rsi:.2f}")

                # RSI > 100 - threshold → overbought → SELL
                elif self.bought[symbol] and rsi > (100 - self.threshold):
                    quantity = self.portfolio.current_positions[symbol]
                    if quantity > 0:
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = False

                        new_row = pd.DataFrame({'Signal': [-quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat(
                            [self.signals[symbol], new_row], ignore_index=True
                        )
                        if self.verbose:
                            print(f"[RSI] SELL {symbol} @ {price} RSI={rsi:.2f}")
                    