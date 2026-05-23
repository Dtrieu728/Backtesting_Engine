import numpy as np 
import pandas as pd 

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on the returns and the number of periods

    Args:
        returns (_type_): _description_
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(equity_curve):
    """
    Create the drawdown curve for the strategy, based on the equity curve

    Args:
        equity_curve (_type_): _description_
    """
    
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index=eq_idx, dtype = float)
    duration = pd.Series(index=eq_idx, dtype = float)
    
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve.iloc[t])
        hwm.append(cur_hwm)
        drawdown.iloc[t] = hwm[t] - equity_curve.iloc[t]
        duration.iloc[t] = 0 if drawdown.iloc[t] == 0 else duration.iloc[t-1] + 1
    return drawdown, duration