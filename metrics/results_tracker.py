import pandas as pd

class ResultsTracker:
    def __init__(self):
        self.results = {}
        
    def add_strategy_results(self, name, equity_curve):
        self.results[name] = pd.Series(equity_curve)
    
    def get_all(self):
        return self.results