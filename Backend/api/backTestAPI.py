import os
import uuid
from pydantic import BaseModel, field_validator
from queue import Queue
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import math

from db.database import SessionLocal
from db.models import BacktestRun
from data.Processed.data_handler import HistoricCSVDataHandler
from strategies.moving_average import MovingAveragesLongShortStrategy, MovingAveragesLongStrategy
from strategies.strategy import BuyAndHoldStrategy
from execution.execution import SimulatedExecutionHandler
from portfolio.portfolio import NaivePortfolio

load_dotenv()

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_dir = os.path.join(BASE_DIR, 'data', 'raw')

class BacktestConfig(BaseModel):
    symbols: list[str]
    strategy: str
    short_period: int = 20
    long_period: int = 50
    initial_capital: float = 100000.0
    version: int = 1
    
    @field_validator('symbols')
    @classmethod
    def symbols_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('symbols must not be empty')
        return v
    

def clean_floats(values: list) -> list:
    """Replace NaN/inf with None so JSON serialization doesn't fail"""
    return [None if (v is None or math.isnan(v) or math.isinf(v)) else v for v in values]

def execute_backtest(run_id: str, config: BacktestConfig):
    db = SessionLocal()
    try:
        run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        if run is None:
            print(f"Run {run_id} not found")
            return
        run.status = "running"
        db.commit()

        events = Queue()
        data = HistoricCSVDataHandler(events, csv_dir, config.symbols)
        portfolio = NaivePortfolio(data, events, initial_capital=config.initial_capital)
        execution = SimulatedExecutionHandler(events)
        strategy = get_strategy(config, data, events, portfolio)

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
        equity_curve = clean_floats(portfolio.equity_curve['equity_curve'].tolist())

        run.status = "complete"
        run.stats = dict(stats)
        run.equity_curve = equity_curve
        db.commit()
        print(f"Backtest {run_id} complete")

    except Exception as e:
        import traceback
        print(f"Backtest error for {run_id}:")
        traceback.print_exc()
        try:
            run.status = "error"
            db.commit()
        except Exception:
            pass
    finally:
        db.close()

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
    db = SessionLocal()
    run = BacktestRun(
        strategy=config.strategy,
        symbols=config.symbols,
        short_period=config.short_period,
        long_period=config.long_period,
        initial_capital=config.initial_capital,
        status="pending"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    run_id = str(run.id)
    db.close()

    background_tasks.add_task(execute_backtest, run_id, config)
    return {"run_id": run_id, "status": "pending"}

@router.get("/backtest/history")
async def get_backtest_history():
    db = SessionLocal()
    runs = db.query(BacktestRun).order_by(BacktestRun.created_at.desc()).limit(20).all()
    db.close()
    return [
        {
            "run_id": str(r.id),
            "strategy": r.strategy,
            "symbols": r.symbols,
            "short_period": r.short_period,
            "long_period": r.long_period,
            "status": r.status,
            "stats": r.stats,
            "created_at": str(r.created_at),
        }
        for r in runs
    ]


@router.get("/backtest/{run_id}")
async def get_backtest_status(run_id: str):
    db = SessionLocal()
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
    db.close()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "status": run.status,
        "stats": run.stats,
        "equity_curve": run.equity_curve,
        "created_at": run.created_at,
    }

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