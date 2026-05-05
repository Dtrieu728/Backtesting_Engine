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


def window_sharpes(results, strategy_name):
    import numpy as np

    sharpes = []

    for r in results:
        equity_dict = r["equity"]

        if strategy_name not in equity_dict:
            sharpes.append(0)
            continue

        equity = np.asarray(equity_dict[strategy_name], dtype=float)

        if len(equity) < 2:
            sharpes.append(0)
            continue

        returns = np.diff(equity) / (equity[:-1] + 1e-9)

        sharpe = np.mean(returns) / (np.std(returns) + 1e-9)

        sharpes.append(sharpe)

    return sharpes

def overall_performance(results):
    full_equity = []

    for r in results:
        strat = r["strategy"]
        eq = np.array(r["equity"][strat])

        eq = eq / eq[0]  # normalize

        if len(full_equity) == 0:
            full_equity.extend(eq)
        else:
            full_equity.extend(eq * full_equity[-1])

    returns = np.diff(full_equity) / (np.array(full_equity[:-1]) + 1e-9)

    return {
        "sharpe": sharpe(returns),
        "max_dd": max_drawdown_curve(full_equity),
        "final_return": full_equity[-1] - 1
    }