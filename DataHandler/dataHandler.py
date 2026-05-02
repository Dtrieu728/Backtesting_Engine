import pandas as pd

class DataHandler:
    def stream_next(self):
        raise NotImplementedError
    

class HistoricCSVDataHandler(DataHandler):
    def __init__(self,events, symbol_list,csv_dir):
        self.events = events
        self.symbol_list = symbol_list 
        self.csv_dir = csv_dir
        self.data = {} 
        self.latest_data = {symbol: [] for symbol in symbol_list}
        self._load_data()
    
    def _load_data(self):
        for symbol in self.symbol_list:
            df = pd.read_csv(f"{self.csv_dr}/{symbol}.csv",parse_date =True,index_col=0)
            df.sort_index(inplace=True)
            self.data[symbol] = df.iterrows()