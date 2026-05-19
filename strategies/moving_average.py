from strategies.strategy import Strategy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from datetime import datetime
from matplotlib import style
from event import SignalEvent




class MovingAverageLongStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period,verbose=False,version = 1):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.name = "Moving Average Crossover Strategy"
        self.verbose = verbose
        self.version = version
        self.short = short_period
        self.long = long_period
        
        
        self.signals = self._set_signals()
        self.strategy = self._set_strategy()
        self.bought = self._setup_initial_bought()
        
    def _set_signals(self):
        signals ={}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date','Signal'])
        return signals
    
    def _set_strategy(self):
        strategy = {}
        for symbol in self.symbol_list:
            strategy[symbol] = pd.DataFrame(columns=['Date','Short_MA','Long_MA'])
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
            price_short = df['Close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()[-1]
            price_long = df['Close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()[-1]
        else:
            price_short = df['Close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()[-1]
            price_long = df['Close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()[-1]

        return price_short, price_long
    
    
    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=-1)
                df = pd.DataFrame(data, columns=['Symbol','Date','Close'])
                df = df.drop(['Symbol'], axis=1)
                df.set_index('Date', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    date = df.index.values[-1]
                    price = df['Close'][-1]
                    self.strategy[symbol] = self.strategy[symbol].append({'Date': date, 'Short': price_short, 'Long': price_long}, ignore_index=True)
                    if self.bought[symbol] == False and price_short > price_long:
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / price)
                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        self.signals[symbol] = self.signals[symbol].append({'Signal': quantity, 'Date': date}, ignore_index=True)
                        if self.verbose: print("Long", date, price)
                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = False
                        self.signals[symbol] = self.signals[symbol].append({'Signal': -quantity, 'Date': date}, ignore_index=True)
                        if self.verbose: print("Exit", date, price)
