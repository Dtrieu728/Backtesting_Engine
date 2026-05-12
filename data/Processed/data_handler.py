import datetime
import pandas as pd
import yfinance as yf
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