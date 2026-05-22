import os
from queue import Queue

from data.Processed.data_handler import HistoricCSVDataHandler
from strategies.strategy import BuyAndHoldStrategy
from strategies.moving_average import MovingAveragesLongShortStrategy
from execution.execution import SimulatedExecutionHandler
from portfolio.portfolio import NaivePortfolio
from core.event import MarketEvent, SignalEvent, OrderEvent, FillEvent
from utils.visualization import plot_equity_curves


def main():
    base = os.path.dirname(__file__)
    csv_dir = os.path.join(base, 'data', 'raw')
    
    user_input = input('Enter the symbols to backtest, separated by commas (e.g. AAPL,GOOG,MSFT): ')
    symbols = [s.strip().upper() for s in user_input.split(',')]
    
    for symbol in symbols:
        file_path = os.path.join(csv_dir, f'{symbol}.csv')
        if not os.path.isfile(file_path):
            raise RuntimeError(f'CSV file for symbol {symbol} not found in {csv_dir}')
        
    if not symbols:
        raise RuntimeError('No CSV files found in data/raw')

    events = Queue()

    data = HistoricCSVDataHandler(events, csv_dir, symbols)
    # strategy = BuyAndHoldStrategy(data, events)
    portfolio = NaivePortfolio(data, events)
    execution = SimulatedExecutionHandler(events)
    strategy = MovingAveragesLongShortStrategy(data, events, short_period=20, long_period=50, portfolio=portfolio)

    # Event loop
    while data.continue_backtest:
        data.update_latest_data()

        while not events.empty():
            event = events.get()
            
            if event is None:
                continue

            if event.type == 'MARKET':
                # update time index in portfolio
                portfolio.update_timeindex(event)
                # allow strategy to see market event and emit signals
                strategy.calculate_signals(event)

            elif event.type == 'SIGNAL':
                portfolio.update_signal(event)

            elif event.type == 'ORDER':
                execution.execute_order(event)

            elif event.type == 'FILL':
                portfolio.update_fill(event)

    # finished
    try:
        strategy.plot_strategy()
        portfolio.create_equity_curve_dataframe()
        stats = portfolio.output_summary_stats()
        print(stats)

        equity_curve = portfolio.equity_curve['equity_curve'].tolist()
        plot_equity_curves({'Buy and Hold': equity_curve})
    except Exception as e:
        import traceback
        print('Finished backtest, but failed to produce summary:')
        traceback.print_exc()


if __name__ == '__main__':
    main()
