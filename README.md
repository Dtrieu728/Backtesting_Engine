# Backtesting_Engine
Backtesting_Engine Side project

## Overview
This is an event-driven backtesting engine for trading strategies. It simulates trading on historical data using an event queue system.

## Components
- **events.py**: Defines event classes (MarketEvent, SignalEvent, OrderEvent, FillEvent)
- **DataHandler/**: Handles loading and streaming market data
- **strategy.py**: Base strategy class and example BuyAndHoldStrategy
- **portfolio.py**: Manages positions and portfolio value
- **execution.py**: Simulates order execution
- **backtester.py**: Main backtesting orchestration

## Usage
1. Prepare CSV data files in a directory (e.g., `data/AAPL.csv` with columns: Date, Open, High, Low, Close, Volume)
2. Update `csv_dir` in `main.py` to point to your data directory
3. Update `symbol_list` with your symbols
4. Run `python main.py`

## Extending
- Create new strategies by inheriting from `Strategy`
- Implement custom portfolio management in `Portfolio`
- Add realistic execution simulation in `ExecutionHandler` 
