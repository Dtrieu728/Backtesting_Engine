import numpy as np

def compute_returns(equity_curve):
    return np.diff(equity_curve) / equity_curve[:-1]

def sharpe_ratio(returns):
    return np.mean(returns) / np.std(returns)

def max_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0

    for x in equity_curve:
        peak = max(peak, x)
        dd = (peak - x) / peak
        max_dd = max(max_dd, dd)

    return max_dd