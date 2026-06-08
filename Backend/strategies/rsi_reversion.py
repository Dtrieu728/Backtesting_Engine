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
                            
                            
def plot_strategy(self):
        style.use('ggplot')
        for symbol in self.symbol_list:
            sig_df = self.signals[symbol].set_index('Date').sort_index()

            # price data
            df = self.data.all_data[symbol].copy()
            if 'Date' in df.columns:
                df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            df.columns = ['Price']

            # RSI over full price history
            delta    = df['Price'].diff()
            gain     = delta.clip(lower=0)
            loss     = -delta.clip(upper=0)
            avg_gain = gain.ewm(com=self.period - 1, min_periods=self.period).mean()
            avg_loss = loss.ewm(com=self.period - 1, min_periods=self.period).mean()
            avg_loss = avg_loss.replace(0, 1e-10)
            df['RSI'] = 100 - (100 / (1 + avg_gain / avg_loss))

            buy_index  = sig_df[sig_df['Signal'] > 0].index
            sell_index = sig_df[sig_df['Signal'] < 0].index

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

            # price + signals
            df['Price'].plot(ax=ax1, color='dodgerblue', linewidth=1.0, label='Price')
            ax1.plot(buy_index,  df.loc[buy_index,  'Price'], '^', markersize=10, color='g', label='Buy')
            ax1.plot(sell_index, df.loc[sell_index, 'Price'], 'v', markersize=10, color='r', label='Sell')
            ax1.set_title(f"{self.name} - {symbol}")
            ax1.set_ylabel('Price')
            ax1.legend()

            # RSI panel
            df['RSI'].plot(ax=ax2, color='purple', linewidth=1.0, label='RSI')
            ax2.axhline(self.threshold,           color='green', linestyle='--', label=f'Oversold ({self.threshold})')
            ax2.axhline(100 - self.threshold,     color='red',   linestyle='--', label=f'Overbought ({100 - self.threshold})')
            ax2.set_ylabel('RSI')
            ax2.set_xlabel('Date')
            ax2.set_ylim(0, 100)
            ax2.legend()

            plt.tight_layout()

        plt.show()