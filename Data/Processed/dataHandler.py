import pandas as pd
from ..events import MarketEvent

class DataHandler:
    def __init__(self,file_path):
        self.data = pd.read_csv(file_path,parse_dates=True,index_col=0)
    
    def get_latest_price(self,symbol,time):
        return self.data.loc[time,symbol]
        
    def get_update(self):
        return self.data
    
    def get_latest_bar(self,symbol,time):
        return self.data.loc[:time].iloc[-1]