import pandas as pd
import yfinance as yf
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))
class DataHandler:
    def __init__(self,file_path):
        self.data = pd.read_csv(
            file_path,
            index_col=0,
            parse_dates=True,
            date_format='%Y-%m-%d')
        
        self.data.columns=self.data.columns.str.strip().str.lower()
        
        self.data = self.data.apply(pd.to_numeric, errors='coerce')
        
        self.data = self.data.dropna()
        
    def get_data(self):
        return self.data
    
    def get_latest_bar(self,symbol,time):
        return self.data.loc[:time].iloc[-1]
    
    

def load_market_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data.to_csv(os.path.join(curr_dir,"../raw",f"{symbol}.csv"))
    
        