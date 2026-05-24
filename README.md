# Backtesting_Engine
Backtesting_Engine Side project

## Live Demo:
[Vercel Link](https://backtesting-engine.vercel.app/)

## Overview
This is an event-driven backtesting engine for trading strategies. It simulates trading on historical data using an event queue system.
-  Strict no-lookahead simulation: only historical data up to time t is used

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


## Work-in progress features
- [ ] Walk forward Testing
- [ ] Live data via yfinance — type any ticker instead of using CSVs
- [ ] Drawdown chart — visualize drawdown over time below the equity curve
- [ ] Parameter sweep — find optimal EMA periods automatically

