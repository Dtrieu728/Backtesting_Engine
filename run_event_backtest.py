import os
from queue import Queue

from data.Processed.data_handler import HistoricCSVDataHandler
from strategies.strategy import BuyAndHoldStrategy
from execution.execution import SimulatedExecutionHandler
from portfolio.portfolio import NaivePortfolio
from core.eventDriven import MarketEvent, SignalEvent, OrderEvent, FillEvent
from utils.visualization import plot_equity_curves


def main():
    base = os.path.dirname(__file__)
    csv_dir = os.path.join(base, 'data', 'raw')
    symbols = [f[:-4] for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if not symbols:
        raise RuntimeError('No CSV files found in data/raw')

    events = Queue()

    data = HistoricCSVDataHandler(events, csv_dir, symbols)
    strategy = BuyAndHoldStrategy(data, events)
    portfolio = NaivePortfolio(data, events)
    execution = SimulatedExecutionHandler(events)

    # Event loop
    while data.continue_backtest:
        data.update_bars()

        while not events.empty():
            event = events.get()

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
