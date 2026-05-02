import pandas as pd


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