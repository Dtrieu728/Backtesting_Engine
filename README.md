# Backtesting_Engine
Backtesting_Engine Side project

## Live Demo:
[Vercel Link](https://backtesting-engine.vercel.app/)

[C++ market simulatorLink](https://github.com/Dtrieu728/market-sim)

## Backtesting Engine Overview
This is an event-driven backtesting engine for trading strategies. It simulates trading on historical data using an event queue system.
-  Strict no-lookahead simulation: only historical data up to time t is used.
-  Walk-forward optimizer: breaks down the data into different sections and then optimizes the strategy on each section. It then takes the best strategy and exports it to the database.


## Overall Pipeline (Backtest -> C++ Market Simulator)
Step 1 — Research (Python Backtester) Run the strategy against years of historical data instantly. Tune the parameters — short period, long period, threshold. Check the Sharpe ratio, max drawdown, win rate.
Step 2 — Validate (C++ Simulator in replay mode) Feed the same historical CSV into the C++ simulator via Phase 7 replay mode. The strategy now runs tick by tick without seeing ahead. If the results roughly match the backtester, the strategy is sound. If they diverge significantly, there's overfitting or a look-ahead bias in the backtest.
Step 3 — Live simulation (C++ Simulator in random walk mode) Switch to real-time random walk prices. The strategy now operates with no knowledge of what comes next, competing against the order book, with threading, latency, and partial fills all in play. This is as close to live trading as the simulator gets.


---

## Installation
All required libraries needed are in the requirements.txt, run this command in the terminal to install required libraries

```
python3 -m pip install -r requirements.txt
```


## Components
- **events.py**: Defines event classes (MarketEvent, SignalEvent, OrderEvent, FillEvent)
- **DataHandler.py**: Handles loading and streaming market data
- **strategy.py**: Base strategy class and example BuyAndHoldStrategy
- **portfolio.py**: Manages positions and portfolio value
- **execution.py**: Simulates order execution
- **backtester.py**: Main backtesting orchestration


## Extending
- Create new strategies by inheriting from `Strategy`
- Implement custom portfolio management in `Portfolio`
- Add realistic execution simulation in `ExecutionHandler` 


