import numpy as np

def compute_returns(equity_curve):
    returns ={}
    for name, curve in equity_curve.items():
        returns[name] = np.diff(curve) / curve[:-1]
    return returns

def sharpe_ratio(returns_dict, periods_per_year=252):
    results = {}

    for name, returns in returns_dict.items():
        returns = np.array(returns)

        if len(returns) < 2 or np.std(returns) == 0:
            results[name] = {
                "sharpe": 0,
                "mean": 0,
                "vol": 0
            }
        else:
            mean = np.mean(returns)
            std = np.std(returns)

            results[name] = {
                "sharpe": (mean / std) * np.sqrt(periods_per_year),
                "mean": mean,
                "vol": std
            }

    return results

def max_drawdown(equity_dict):
    drawdowns = {}

    for name, curve in equity_dict.items():
        curve = np.array(curve)

        peak = np.maximum.accumulate(curve)
        dd = (curve - peak) / peak

        drawdowns[name] = np.min(dd)

    return drawdowns