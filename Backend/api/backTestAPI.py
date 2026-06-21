import os
from itertools import product
from pydantic import BaseModel, field_validator
from queue import Queue
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import math
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session
import json
from datetime import datetime

from db.database import SessionLocal
from db.models import BacktestRun
from metrics.performance import create_sharpe_ratio
from data.Processed.data_handler import HistoricCSVDataHandler
from strategies.moving_average import MovingAveragesLongShortStrategy, MovingAveragesLongStrategy,MovingAveragesMomentumStrategy
from strategies.rsi_reversion import RSIMeanReversionStrategy
from strategies.strategy import BuyAndHoldStrategy
from execution.execution import SimulatedExecutionHandler
from portfolio.portfolio import NaivePortfolio
from core.event import MarketEvent

load_dotenv()

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_dir = os.path.join(BASE_DIR, 'data', 'raw')

try:
    from api.backTestAPI import router
    app.include_router(router, prefix="/api")
    print("Router loaded successfully")
except Exception as e:
    import traceback
    print("Router failed to load!")
    traceback.print_exc()

class BacktestConfig(BaseModel):
    symbols: list[str]
    strategy: str
    short_period: int = 20
    long_period: int = 50
    initial_capital: float = 100000.0
    version: int = 1
    use_live_data:bool = False
    start_date: str = '2010-01-01'
    
    @field_validator('symbols')
    @classmethod
    def symbols_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('symbols must not be empty')
        return v
class WalkForwardConfig(BaseModel):
    symbols: list[str]
    strategy: str
    initial_capital: float = 100000.0
    use_live_data:bool = False
    start_date: str = '2010-01-01'
    train_years: int = 3
    test_years: int = 1
    short_periods: list[int] = [10,20,30,50]
    long_periods: list[int] = [50,100,150,200]
    
    @field_validator('symbols')
    @classmethod
    def symbols_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('symbols must not be empty')
        return v
def run_single_backtest(data_df,symbols,strategy_name,short_period,long_period,initial_capital):
    """
    Run One back test on a dataframe slice and return sharpe ratio and equity curve

    Args:
        data_df (_type_): _description_
        symbols (_type_): _description_
        strategy_name (_type_): _description_
        short_period (_type_): _description_
        long_period (_type_): _description_
        initial_capital (_type_): _description_
    """
    from io import StringIO
    events = Queue()
    
    class SliceDataHandler:
        def __init__(self,df,symbol_list):
            self.symbol_list = symbol_list
            self.latest_symbol_data = {s: [] for s in symbol_list}
            self.all_data = {}
            self.symbol_generators = {}
            self.continue_backtest = True
            self.time_col = 1
            self.price_col = 2
            self.start_date = df.index[0]
            
            for symbol in symbol_list:
                self.all_data[symbol] = df[[symbol]].copy()
                self.all_data[symbol].columns = ['close']
                self.symbol_generators[symbol] = self._gen(symbol,df)
        
        def _gen(self,symbol,df):
            for date,row in df.iterrows():
                yield (symbol,date,float(row[symbol]))
        def get_latest_data(self, symbol, N=1):
            return self.latest_symbol_data[symbol][-N:]
        
        def update_latest_data(self):
            for symbol in self.symbol_list:
                try:
                    data = next(self.symbol_generators[symbol])
                    self.latest_symbol_data[symbol].append(data)
                except StopIteration:
                    self.continue_backtest = False
            events.put(MarketEvent())
                
                
    data = SliceDataHandler(data_df,symbols)
    portfolio = NaivePortfolio(data, events, initial_capital=initial_capital)
    execution = SimulatedExecutionHandler(events)
    
    config_obj = type('cfg', (),{
        'strategy':strategy_name,
        'short_period':short_period,
        'long_period':long_period,
    })()
    strategy = get_strategy(config_obj, data, events, portfolio)
    
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
    returns = portfolio.equity_curve['returns']
    sharpe = float(create_sharpe_ratio(returns))
    equity_curve = portfolio.equity_curve['equity_curve'].to_list()
    return sharpe, equity_curve
            
def execute_walk_forward(run_id: str, config: WalkForwardConfig):
    db = SessionLocal()
    try:
        run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        run.status = "running"
        db.commit()

        # Load full price data
        if config.use_live_data:
            full_df = yf.download(
                config.symbols,
                start=config.start_date,
                auto_adjust=True,
                progress=False
            )['Close']
        else:
            frames = {}
            for symbol in config.symbols:
                path = os.path.join(csv_dir, f'{symbol}.csv')
                tmp = pd.read_csv(path, index_col=0, parse_dates=True).iloc[::-1]
                tmp.columns = tmp.columns.str.strip()
                frames[symbol] = pd.to_numeric(
                    tmp['Close'].astype(str).str.replace('$','').str.replace(',',''),
                    errors='coerce'
                )
            full_df = pd.DataFrame(frames).dropna()

        if isinstance(full_df, pd.Series):
            full_df = full_df.to_frame(config.symbols[0])

        full_df = full_df.dropna()
        full_df.index = pd.to_datetime(full_df.index)
        full_df = full_df.sort_index()

        train_days = config.train_years * 252
        test_days = config.test_years * 252
        window_size = train_days + test_days
        combined_oos_curve = []
        window_stats = []

        i = 0
        while i + window_size <= len(full_df):
            train_df = full_df.iloc[i: i + train_days]
            test_df = full_df.iloc[i + train_days: i + window_size]

            # Grid search on training window
            best_sharpe = -999
            best_short = config.short_periods[0]
            best_long = config.long_periods[0]

            for short, long in product(config.short_periods, config.long_periods):
                if short >= long:
                    continue
                try:
                    sharpe, _ = run_single_backtest(
                        train_df, config.symbols, config.strategy,
                        short, long, config.initial_capital
                    )
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_short = short
                        best_long = long
                except Exception:
                    continue

            # Run on test window with best params
            _, oos_curve = run_single_backtest(
                test_df, config.symbols, config.strategy,
                best_short, best_long, config.initial_capital
            )

            window_stats.append({
                "window": i // test_days + 1,
                "train_start": str(train_df.index[0].date()),
                "train_end": str(train_df.index[-1].date()),
                "test_start": str(test_df.index[0].date()),
                "test_end": str(test_df.index[-1].date()),
                "best_short": best_short,
                "best_long": best_long,
                "in_sample_sharpe": round(best_sharpe, 3),
            })

            # Scale OOS curve to continue from last value
            if combined_oos_curve:
                scale = combined_oos_curve[-1]
                oos_curve = [v * scale for v in oos_curve]

            combined_oos_curve.extend(oos_curve)
            i += test_days

        combined_oos_curve = clean_floats(combined_oos_curve)
        final_return = (combined_oos_curve[-1] - 1) * 100 if combined_oos_curve else 0

        stats = {
            "Total Return": f"{final_return:.2f}%",
            "Windows": str(len(window_stats)),
            "Train Years": str(config.train_years),
            "Test Years": str(config.test_years),
        }

        run.status = "complete"
        run.stats = stats
        run.equity_curve = combined_oos_curve
        db.commit()
        print(f"Walk forward {run_id} complete — {len(window_stats)} windows")

    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            run.status = "error"
            db.commit()
        except Exception:
            pass
    finally:
        db.close()

@router.post("/walkforward")
async def run_walk_forward(config: WalkForwardConfig, background_tasks: BackgroundTasks):
    db = SessionLocal()
    run = BacktestRun(
        strategy=f"walk_forward_{config.strategy}",
        symbols=config.symbols,
        short_period=config.short_periods[0],
        long_period=config.long_periods[0],
        initial_capital=config.initial_capital,
        status="pending"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    run_id = str(run.id)
    db.close()

    background_tasks.add_task(execute_walk_forward, run_id, config)
    return {"run_id": run_id, "status": "pending"}

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
        
        if config.use_live_data:
            from data.Processed.data_handler import YFinanceDataHandler
            data = YFinanceDataHandler(events, config.symbols,start_date=config.start_date)
        else:
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
    elif config.strategy == 'momentum':
        return MovingAveragesMomentumStrategy(data, events, portfolio, config.short_period, config.long_period)
    elif config.strategy == 'buy_and_hold':
        return BuyAndHoldStrategy(data, events)
    elif config.strategy.startswith('rsi'):
        return RSIMeanReversionStrategy(data, events, portfolio,period=config.short_period, threshold=config.long_period)
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
        "id": str(run.id),
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
        {"id": "momentum", "name": "Moving Averages Momentum"},
        {"id": "buy_and_hold", "name": "Buy and Hold"},
        {"id": "rsi", "name": "RSI Mean Reversion"},
    ]

@router.get("/symbols")
async def get_symbols():
    """Returns available symbols based on CSV files present in data/raw"""
    available = [f.replace('.csv', '') for f in os.listdir(csv_dir) if f.endswith('.csv')]
    return {"symbols": available}

@router.get("/ticker/{symbol}")
async def validate_ticker(symbol: str):
    """
    Checks if a ticker is valid and returns basic info about it such as name
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        if not info or info.get("regularMarketPrice") is None:
            raise HTTPException(status_code=404, detail="Ticker not found")
        return {
            "symbol": symbol.upper(),
            "name": info.get("shortName", symbol),
            "price": info.get("regularMarketPrice"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail= f"{symbol} not found")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/export")
def export_config(run_id: str, db: Session = Depends(get_db)):
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    config = {
        "strategy": run.strategy,
        "symbols": run.symbols,
        "short_period": run.short_period,
        "long_period": run.long_period,
        "initial_capital": run.initial_capital,
        "sharpe": run.stats.get("Sharpe Ratio") if run.stats else None,
        "exported_at": datetime.utcnow().isoformat()
    }

    with open("strategy_config.json", "w") as f:
        json.dump(config, f, indent=2)

    return config