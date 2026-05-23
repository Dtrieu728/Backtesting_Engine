import os
import uuid
from queue import Queue
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import math

from data.Processed.data_handler import HistoricCSVDataHandler
from strategies.moving_average import MovingAveragesLongShortStrategy, MovingAveragesLongStrategy
from strategies.strategy import BuyAndHoldStrategy
from execution.execution import SimulatedExecutionHandler
from portfolio.portfolio import NaivePortfolio

router = APIRouter()
results_store = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_dir = os.path.join(BASE_DIR, 'data', 'raw')
class BacktestConfig(BaseModel):
    symbols: list[str]
    strategy: str
    short_period: int = 20
    long_period: int = 50
    initial_capital: float = 100000.0
    version: int = 1

def clean_floats(values: list) -> list:
    """Replace NaN/inf with None so JSON serialization doesn't fail"""
    return [None if (v is None or math.isnan(v) or math.isinf(v)) else v for v in values]

def execute_backtest(run_id: str, config: BacktestConfig):
    
    """This runs in the background — keeps the API non-blocking"""
    try:
        results_store[run_id] = {"status": "running"}
        
        # Wire up your existing engine
        events = Queue()
        data = HistoricCSVDataHandler(events, csv_dir, config.symbols)
        portfolio = NaivePortfolio(data, events, initial_capital=config.initial_capital)
        execution = SimulatedExecutionHandler(events)
        strategy = get_strategy(config, data, events, portfolio)

        # Your existing event loop — untouched
        while data.continue_backtest:
            data.update_latest_data()
            while not events.empty():
                event = events.get()
                if event is None:
                    continue
                if event.type == 'MARKET':
                    portfolio.update_timeindex(event)
                    strategy.calculate_signals(event)
                elif event.type == 'SIGNAL':
                    portfolio.update_signal(event)
                elif event.type == 'ORDER':
                    execution.execute_order(event)
                elif event.type == 'FILL':
                    portfolio.update_fill(event)

        portfolio.create_equity_curve_dataframe()
        stats = portfolio.output_summary_stats()
        
        equity_curve = portfolio.equity_curve['equity_curve'].tolist()

        results_store[run_id] = {
            "status": "complete",
            "stats": dict(stats),
            "equity_curve": clean_floats(equity_curve),
            "signals": {s: strategy.signals[s].to_dict() for s in config.symbols}
        }
    except Exception as e:
        results_store[run_id] = {"status": "error", "detail": str(e)}

def get_strategy(config, data, events, portfolio):
    """Maps strategy name from request to strategy class"""
    if config.strategy == 'long_only':
        return MovingAveragesLongStrategy(data, events, portfolio, config.short_period, config.long_period)
    elif config.strategy == 'long_short':
        return MovingAveragesLongShortStrategy(data, events, portfolio, config.short_period, config.long_period)
    elif config.strategy == 'buy_and_hold':
        return BuyAndHoldStrategy(data, events)
    else:
        raise ValueError(f"Unknown strategy: {config.strategy}")

@router.post("/backtest")
async def run_backtest(config: BacktestConfig, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    background_tasks.add_task(execute_backtest, run_id, config)
    return {"run_id": run_id, "status": "pending"}

@router.get("/backtest/{run_id}")
async def get_backtest_status(run_id: str):
    result = results_store.get(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return result

@router.get("/strategies")
async def get_strategies():
    return [
        {"id": "long_only", "name": "Moving Averages Long Only"},
        {"id": "long_short", "name": "Moving Averages Long Short"},
        {"id": "buy_and_hold", "name": "Buy and Hold"},
    ]

@router.get("/symbols")
async def get_symbols():
    """Returns available symbols based on CSV files present in data/raw"""
    available = [f.replace('.csv', '') for f in os.listdir(csv_dir) if f.endswith('.csv')]
    return {"symbols": available}