import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os 


current_dir = os.path.dirname(os.path.abspath(__file__))

def build_full_equity(results, strategy_name):
    full_curve = []

    for r in results:
        if strategy_name not in r["equity"]:
            continue

        curve = np.array(r["equity"][strategy_name], dtype=float)

        if len(full_curve) == 0:
            full_curve.extend(curve)
        else:
            # stitch by scaling to last value
            scale = full_curve[-1] / curve[0]
            full_curve.extend(curve * scale)

    return np.array(full_curve)

def plot_equity_curves(results, strategies):
    plt.figure(figsize=(12,6))

    for strat in strategies:
        curve = build_full_equity(results, strat)
        plt.plot(curve, label=strat)

    plt.title("Strategy Comparison (Walk-Forward)")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid(True)

    plt.savefig(os.path.join(current_dir, "plots", "comparison.png"))
    plt.show()
    

def plot_equity(results, strategy_name):
    os.makedirs(os.path.join(current_dir, "plots"), exist_ok=True)

    curve = build_full_equity(results, strategy_name)

    plt.figure(figsize=(12,6))
    plt.plot(curve, linewidth=2)

    plt.title(f"{strategy_name.upper()} Equity Curve (Walk-Forward)")
    plt.xlabel("Time")
    plt.ylabel("Portfolio Value")
    plt.grid(True)

    plt.savefig(os.path.join(current_dir, "plots", f"{strategy_name}_equity.png"))
    plt.show()

def plot_turnover(results, strategy_name):
    turnover_full = []

    for r in results:
        if strategy_name not in r["turnover"]:
            continue

        turnover_full.extend(r["turnover"][strategy_name])

    turnover_full = np.array(turnover_full)

    plt.figure(figsize=(12,6))
    plt.plot(turnover_full, alpha=0.7)

    plt.title(f"{strategy_name.upper()} Turnover Over Time")
    plt.xlabel("Time")
    plt.ylabel("Turnover")
    plt.grid(True)

    plt.savefig(os.path.join(current_dir, "plots", f"{strategy_name}_turnover.png"))
    plt.show()
    
    
def performance_summary(results, strategy_name):
    curve = build_full_equity(results, strategy_name)

    returns = np.diff(curve) / (curve[:-1] + 1e-9)
    sharpe = np.mean(returns) / (np.std(returns) + 1e-9)

    peak = np.maximum.accumulate(curve)
    dd = np.min((curve - peak) / (peak + 1e-9))

    return {
        "sharpe": sharpe,
        "max_drawdown": dd,
        "final_value": curve[-1]
    }

def plot_portfolio_value(results, strategy_name, initial_cash=100000):
    curve = build_full_equity(results, strategy_name)

    # normalize to starting capital
    curve = curve / curve[0] * initial_cash

    plt.figure(figsize=(12,6))
    plt.plot(curve, linewidth=2)

    plt.title(f"{strategy_name.upper()} Portfolio Value")
    plt.xlabel("Time")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)

    plt.savefig(os.path.join(current_dir, "plots", f"{strategy_name}_portfolio.png"))
    plt.show()
    