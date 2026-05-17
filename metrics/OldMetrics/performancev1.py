import numpy as np

def compute_returns(equity_curve):
    returns ={}
    for name, curve in equity_curve.items():
        returns[name] = np.diff(curve) / curve[:-1]
    return returns

def sharpe_ratio(returns_dict, periods_per_year=252):
    results = {}

    for name, returns in returns_dict.items():
        returns = np.asarray(returns)

        if len(returns) < 2:
            results[name] = {"sharpe": 0, "mean": 0, "vol": 0}
            continue

        mean = np.mean(returns)
        vol = np.std(returns, ddof=1)

        if vol == 0:
            sharpe = 0
        else:
            sharpe = (mean / vol) * np.sqrt(periods_per_year)

        results[name] = {
            "sharpe": sharpe,
            "mean": mean,
            "vol": vol
        }

    return results


def max_drawdown(equity_dict):
    drawdowns = {}

    for name, curve in equity_dict.items():
        curve = np.asarray(curve)

        if len(curve) == 0:
            drawdowns[name] = 0
            continue

        peak = np.maximum.accumulate(curve)

        dd = np.zeros_like(curve)
        valid = peak != 0

        dd[valid] = (curve[valid] - peak[valid]) / peak[valid]

        drawdowns[name] = np.min(dd)

    return drawdowns

def max_drawdown_curve(curve):
    curve = np.asarray(curve)

    if len(curve) == 0:
        return 0

    peak = np.maximum.accumulate(curve)
    dd = (curve - peak) / (peak + 1e-9)

    return np.min(dd)


def window_sharpes(results, strategy_name=None):
    sharpes = []
    for r in results:
        equity = r["equity"]
        
        if isinstance(equity, dict):
            if strategy_name not in equity:
                sharpes.append(0.0)
                continue
            equity = equity[strategy_name]
        
        equity = np.asarray(equity, dtype=float)
        if len(equity) < 2:
            sharpes.append(0.0)
            continue

        returns = np.diff(equity) / (equity[:-1] + 1e-9)
        vol = np.std(returns)
        sharpe = (np.mean(returns) / (vol + 1e-9)) * np.sqrt(252) if vol > 0 else 0.0
        sharpes.append(sharpe)
    return sharpes


def overall_performance(results):

    all_returns = []
    
    for r in results:
        equity = np.asarray(r["equity"], dtype=float)
        if len(equity) < 2:
            continue
        
        window_returns = np.diff(equity) / (equity[:-1] + 1e-9)
        all_returns.extend(window_returns)

    all_returns = np.array(all_returns)
    if len(all_returns) == 0:
        return {"sharpe": 0, "max_dd": 0, "final_return": 0}

    full_equity = np.cumprod(1 + all_returns)
    
    mean_ret = np.mean(all_returns)
    std_ret = np.std(all_returns)
    sharpe = (mean_ret / (std_ret + 1e-9)) * np.sqrt(252)

    return {
        "sharpe": sharpe,
        "max_dd": max_drawdown_curve(full_equity),
        "total_return": full_equity[-1] - 1
    }