import pandas as pd
import matplotlib.pyplot as plt
import math
from datetime import datetime
from matplotlib import style
from core.event import SignalEvent
from strategies.strategy import Strategy

class MovingAveragesLongStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period, verbose=False, version=1):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Long'
        self.verbose = verbose
        self.version = version

        self.signals = self._setup_signals()
        self.strategy = self._setup_strategy()
        self.bought = self._setup_initial_bought()

    def _setup_signals(self):
        signals = {}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date', 'Signal'])

        return signals

    def _setup_strategy(self):
        strategy = {}
        for symbol in self.symbol_list:
            strategy[symbol] = pd.DataFrame(columns=['Date', 'Short', 'Long'])

        return strategy

    def _setup_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_long_short(self, df):
        price_short = None
        price_long = None
        if self.version == 1:
            price_short = df['Close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            price_long = df['Close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()
        else:
            price_short = df['Close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()
            price_long = df['Close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()

        if not price_short.empty and not price_long.empty:
            price_short = price_short.iloc[-1]
            price_long = price_long.iloc[-1]
            
        return price_short, price_long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=len(self.data.latest_symbol_data[symbol]))
                df = pd.DataFrame(data, columns=['Symbol','Date','Close'])
                df = df.drop(['Symbol'], axis=1)
                df.set_index('Date', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    # 1. LONG ENTRY LOGIC
                    if self.bought[symbol] == False and price_short > price_long:
                        current_positions = self.portfolio.current_positions[symbol]
                        # Exit any existing short before going long
                        if current_positions < 0:
                            signal = SignalEvent(symbol, date, 'EXIT', math.fabs(current_positions))
                            self.events.put(signal)
                        
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / price)
                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        
                        new_row = pd.DataFrame({'Signal': [quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat([self.signals[symbol], new_row], ignore_index=True)
                        if self.verbose: print("Long", date, price)

                    # 2. SHORT ENTRY LOGIC (or Exit Long)
                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        # Exit the long
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        
                        self.bought[symbol] = False
                        new_row = pd.DataFrame({'Signal': [-quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat([self.signals[symbol], new_row], ignore_index=True)
                        if self.verbose: print("Short", date, price) 

    def plot_strategy(self):
        style.use('ggplot')
        for symbol in self.symbol_list:
            sig_df = self.signals[symbol].set_index('Date').sort_index(ascending=True)

            # Prepare price data
            df = self.data.all_data[symbol].copy()
            if 'Date' in df.columns:
                df.set_index('Date', inplace=True)
            df.sort_index(ascending=True, inplace=True)
            df.columns = ['Price']

            # Compute EMAs directly from full price history
            df['Short EMA'] = df['Price'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            df['Long EMA'] = df['Price'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()

            short_index = sig_df[sig_df['Signal'] < 0].index
            long_index = sig_df[sig_df['Signal'] > 0].index

            strategy_fig, strategy_ax = plt.subplots()
            df['Price'].plot(ax=strategy_ax, color='dodgerblue', linewidth=1.0, label='Price')
            df['Short EMA'].plot(ax=strategy_ax, color='grey', linewidth=1.0, label=f'EMA {self.short_period}')
            df['Long EMA'].plot(ax=strategy_ax, color='black', linewidth=1.0, label=f'EMA {self.long_period}')

            strategy_ax.plot(short_index, df.loc[short_index, 'Price'], 'v', markersize=10, color='r', label='Short/Exit')
            strategy_ax.plot(long_index, df.loc[long_index, 'Price'], '^', markersize=10, color='g', label='Long')

            strategy_ax.set_title(f"{self.name} - {symbol}")
            strategy_ax.set_xlabel('Time')
            strategy_ax.set_ylabel('Price')
            strategy_ax.legend()

        plt.show()

class MovingAveragesLongShortStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period, version=1,verbose =False):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Long Short'
        self.version = version

        self.signals = self._setup_signals()
        self.strategy = self._setup_strategy()
        self.bought = self._setup_initial_bought()
        self.verbose = verbose

    def _setup_signals(self):
        signals = {}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date', 'Signal'])

        return signals

    def _setup_strategy(self):
        strategy = {}
        for symbol in self.symbol_list:
            strategy[symbol] = pd.DataFrame(columns=['Date', 'Short', 'Long'])

        return strategy

    def _setup_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_long_short(self, df):
        price_short = None
        price_long = None
        if self.version == 1:
            price_short = df['Close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            price_long = df['Close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()
        else:
            price_short = df['Close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()
            price_long = df['Close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()

        if not price_short.empty and not price_long.empty:
            price_short = price_short.iloc[-1]
            price_long = price_long.iloc[-1]
            
        return price_short, price_long
    
    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=len(self.data.latest_symbol_data[symbol]))
                df = pd.DataFrame(data, columns=['Symbol','Date','Close'])
                df = df.drop(['Symbol'], axis=1)
                df.set_index('Date', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    # 1. LONG ENTRY LOGIC
                    if self.bought[symbol] == False and price_short > price_long:
                        current_positions = self.portfolio.current_positions[symbol]
                        # Exit any existing short before going long
                        if current_positions < 0:
                            signal = SignalEvent(symbol, date, 'EXIT', math.fabs(current_positions))
                            self.events.put(signal)
                        
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / price)
                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        
                        new_row = pd.DataFrame({'Signal': [quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat([self.signals[symbol], new_row], ignore_index=True)
                        if self.verbose: print("Long", date, price)

                    # 2. SHORT ENTRY LOGIC (or Exit Long)
                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        # Exit the long
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        # Enter the short
                        signal = SignalEvent(symbol, date, 'SHORT', quantity)
                        self.events.put(signal)
                        
                        self.bought[symbol] = False
                        new_row = pd.DataFrame({'Signal': [-quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat([self.signals[symbol], new_row], ignore_index=True)
                        if self.verbose: print("Short", date, price) 
                        
    def plot_strategy(self):
        style.use('ggplot')
        for symbol in self.symbol_list:
            sig_df = self.signals[symbol].set_index('Date').sort_index(ascending=True)

            # Prepare price data
            df = self.data.all_data[symbol].copy()
            if 'Date' in df.columns:
                df.set_index('Date', inplace=True)
            df.sort_index(ascending=True, inplace=True)
            df.columns = ['Price']

            # Compute EMAs directly from full price history
            df['Short EMA'] = df['Price'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            df['Long EMA'] = df['Price'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()

            short_index = sig_df[sig_df['Signal'] < 0].index
            long_index = sig_df[sig_df['Signal'] > 0].index

            strategy_fig, strategy_ax = plt.subplots()
            df['Price'].plot(ax=strategy_ax, color='dodgerblue', linewidth=1.0, label='Price')
            df['Short EMA'].plot(ax=strategy_ax, color='grey', linewidth=1.0, label=f'EMA {self.short_period}')
            df['Long EMA'].plot(ax=strategy_ax, color='black', linewidth=1.0, label=f'EMA {self.long_period}')

            strategy_ax.plot(short_index, df.loc[short_index, 'Price'], 'v', markersize=10, color='r', label='Short/Exit')
            strategy_ax.plot(long_index, df.loc[long_index, 'Price'], '^', markersize=10, color='g', label='Long')

            strategy_ax.set_title(f"{self.name} - {symbol}")
            strategy_ax.set_xlabel('Time')
            strategy_ax.set_ylabel('Price')
            strategy_ax.legend()

        plt.show()

class MovingAveragesMomentumStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period,version=1, verbose=False):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Momentum'
        self.version =version
        self.verbose = verbose

    def calculate_long_short(self, df):
        if df.empty or len(df) < self.long_period:
            return None, None

        price_short = None
        price_long = None
        
        if self.version == 1:
            short_series = df['Close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            long_series = df['Close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()
        else:
            short_series = df['Close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()
            long_series = df['Close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()

        if not short_series.empty and not long_series.empty:
            price_short = short_series.iloc[-1]
            price_long = long_series.iloc[-1]

        return price_short, price_long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=len(self.data.latest_symbol_data[symbol]))
                df = pd.DataFrame(data, columns=['Symbol','Date','Close'])
                df = df.drop(['Symbol'], axis=1)
                df.set_index('Date', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    diff = price_long - price_short
                    factor = math.fabs(2*math.atan(diff) / math.pi)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    if price_short >= price_long:
                        quantity = math.floor(factor * self.portfolio.current_holdings['cash'] / price)
                        if quantity != 0:
                            signal = SignalEvent(symbol, date, 'LONG', quantity)
                            self.events.put(signal)
                            if self.verbose: print('Long', date, price)
                    else:
                        quantity = math.floor(factor/2 * self.portfolio.current_positions[symbol])
                        if quantity != 0:
                            signal = SignalEvent(symbol, date, 'SHORT', quantity)
                            self.events.put(signal)
                            if self.verbose: print('Short', date, price)
                            
                            
def plot_strategy(self):
    style.use('ggplot')
    for symbol in self.symbol_list:
        # price data
        df = self.data.all_data[symbol].copy()
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        df.sort_index(ascending=True, inplace=True)
        df.columns = ['Price']

        # compute EMAs
        df['Short EMA'] = df['Price'].ewm(
            span=self.short_period, min_periods=self.short_period, adjust=False
        ).mean()
        df['Long EMA'] = df['Price'].ewm(
            span=self.long_period, min_periods=self.long_period, adjust=False
        ).mean()

        # momentum factor over time
        df['Diff']   = df['Long EMA'] - df['Short EMA']
        df['Factor'] = df['Diff'].apply(
            lambda d: abs(2 * math.atan(d) / math.pi)
        )

        # crossover points — where short crosses long
        df['Cross'] = df['Short EMA'] - df['Long EMA']
        cross_above = df[(df['Cross'] > 0) & (df['Cross'].shift(1) <= 0)].index  # bullish
        cross_below = df[(df['Cross'] < 0) & (df['Cross'].shift(1) >= 0)].index  # bearish

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # price + EMAs + crossover markers
        df['Price'].plot(ax=ax1, color='dodgerblue', linewidth=1.0, label='Price')
        df['Short EMA'].plot(ax=ax1, color='grey', linewidth=1.0, label=f'EMA {self.short_period}')
        df['Long EMA'].plot(ax=ax1, color='black', linewidth=1.0, label=f'EMA {self.long_period}')
        ax1.plot(cross_above, df.loc[cross_above, 'Price'], '^', markersize=10, color='g', label='Bullish Cross')
        ax1.plot(cross_below, df.loc[cross_below, 'Price'], 'v', markersize=10, color='r', label='Bearish Cross')
        ax1.set_title(f"{self.name} - {symbol}")
        ax1.set_ylabel('Price')
        ax1.legend()

        # momentum factor panel
        df['Factor'].plot(ax=ax2, color='purple', linewidth=1.0, label='Momentum Factor')
        ax2.axhline(0.5, color='grey', linestyle='--', alpha=0.5, label='0.5 threshold')
        ax2.set_ylabel('Factor (0-1)')
        ax2.set_xlabel('Date')
        ax2.set_ylim(0, 1)
        ax2.legend()

        plt.tight_layout()

    plt.show()