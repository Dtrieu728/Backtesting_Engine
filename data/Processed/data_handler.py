import datetime
import pandas as pd
try:
    import yfinance as yf
except Exception:
    yf = None
import os,os.path
from abc import ABCMeta, abstractmethod
from core.eventDriven import MarketEvent

class DataHandler(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    
    def get_latest_bars(self,symbol,N=1):
        """Returns the last N bars from the latest_symbol list, or fewer if less bars are available

        Args:
            symbol (_type_): Ticker Symbol
            N (int, optional): Number of Bars. Defaults to 1.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError("Should implement get_latest_bars()")
    
    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bar to the latest symbol structure for all symbols in the symbol list
        """
        raise NotImplementedError("Should implement update_bars()")

        
class HistoricCSVDataHandler(DataHandler):
    """HistoricCSVDataHandler is designed to rea CSV files for each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to trading interface
    """
    
    def __init__(self, events, csv_dir, symbol_list):
        """Initialises the historic data handler by requesting the location of the CSV files and a list of symbols
        
        It will be assumed that all files are of the form 'symbol.csv', where symbol is a string in the list

        Args:
            events (_type_): The Event queue
            csv_dir (_type_): Absolute directory path to CSV files
            symbol_list (_type_): A list of symbol strings
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data={}
        self.continue_backtest = True
        
        self._open_convert_csv_files()
        
    def _open_convert_csv_files(self):
        """
        Opens the CSv files from the data directory, converting them into pandas Dataframe within a symbol dictionary
        
        For this handler it will assumed that the data is taken from Yahoo. Thus its format will be respected
        """
        comb_index = None
        # Read each CSV and build combined index
        for s in self.symbol_list:
            csv_path = os.path.join(self.csv_dir, '%s.csv' % s)
            try:
                self.symbol_data[s] = pd.read_csv(
                    csv_path, header=0, index_col=0,
                    parse_dates=True, names=['datetime','open','high','low','close','adj_close','volume']
                )
            except Exception:
                # Fallback for files with extra header rows (repo CSVs)
                self.symbol_data[s] = pd.read_csv(
                    csv_path, header=None, names=['datetime','open','high','low','close','adj_close','volume'],
                    skiprows=3, index_col=0, parse_dates=True
                )
            self.symbol_data[s].sort_index(inplace=True)

            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index = comb_index.union(self.symbol_data[s].index)

        # Initialize latest data containers and align dataframes to combined index
        # Expose a start_date for downstream components
        if comb_index is not None and len(comb_index) > 0:
            self.start_date = comb_index[0]
        else:
            self.start_date = None
        for s in self.symbol_list:
            self.latest_symbol_data[s] = []
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad')
            # Ensure adj_close column exists (might be named 'Adj Close' in some files)
            if 'adj_close' not in self.symbol_data[s].columns and 'Adj Close' in self.symbol_data[s].columns:
                self.symbol_data[s]['adj_close'] = self.symbol_data[s]['Adj Close']
            # Compute returns
            try:
                self.symbol_data[s]['returns'] = self.symbol_data[s]['adj_close'].pct_change()
            except Exception:
                self.symbol_data[s]['returns'] = self.symbol_data[s]['close'].pct_change()
            # Convert to iterator of rows
            self.symbol_data[s] = self.symbol_data[s].iterrows()
    
    def _get_new_bar(self, symbol):
        """Generator that returns the latest bar in the CSV file

        Args:
            symbol (_type_): _description_

        Yields:
            _type_: _description_
        """
        
        for b in self.symbol_data[symbol]:
            idx = b[0]
            row = b[1]
            # idx may be a pandas Timestamp already
            if hasattr(idx, 'to_pydatetime'):
                dt = idx.to_pydatetime()
            else:
                try:
                    dt = datetime.datetime.strptime(str(idx), '%Y-%m-%d %H:%M:%S')
                except Exception:
                    try:
                        dt = datetime.datetime.strptime(str(idx), '%Y-%m-%d')
                    except Exception:
                        dt = None
            yield tuple([symbol, dt, row.get('open'), row.get('high'), row.get('low'), row.get('close'), row.get('adj_close'), row.get('volume')])
            
    def get_latest_bars(self, symbol, N=1):
        """Returns the last N bars from the latest_symbol list, or fewer if less bars are available

        Args:
            symbol (_type_): _description_
            N (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
        else:
            return bars_list[-N:]
    def update_bars(self):
        """Pushes the latest bar to the latest symbol structure for all symbols in the symbol list
        """
        for s in self.symbol_list:
            try:
                bar = self._get_new_bar(s).__next__()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())