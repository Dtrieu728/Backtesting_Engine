import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os 


current_dir = os.path.dirname(os.path.abspath(__file__))

def build_full_equity(results):
    full_curve = []

    for r in results:
        curve_data = r["equity"]
        
        if isinstance(curve_data, dict):
            if not curve_data: continue
            curve = np.array(list(curve_data.values())[0], dtype=float)
        else:
            curve = np.array(curve_data, dtype=float)

        if len(full_curve) == 0:
            full_curve.extend(curve)
        else:
            scale = full_curve[-1] / (curve[0] + 1e-9)
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
    
def plot_switching_performance(results):
    os.makedirs(os.path.join(current_dir, "plots"), exist_ok=True)

    curve = build_full_equity(results)
    
    if len(curve) == 0:
        print("Error: Equity curve is empty. Check if engine is running correctly.")
        return

    plt.figure(figsize=(12,6))
    plt.plot(curve, linewidth=2, color='#2ecc71', label='Regime Switching Model')

    plt.title("Combined Regime-Switching Equity Curve")
    plt.xlabel("Total Trading Days")
    plt.ylabel("Normalized Portfolio Value")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(os.path.join(current_dir, "plots", "switching_equity.png"))
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
    
def plot_equity_with_regimes(results):
    full_curve = build_full_equity(results)
    plt.figure(figsize=(14, 7))
    
    # Plot the line
    plt.plot(full_curve, color='black', lw=1.5)
    
    # Overlay regime colors
    curr_idx = 0
    colors = {"trend": "green", "chop": "yellow", "high_vol": "red"}
    
    for r in results:
        window_len = len(r["equity"])
        regime = r.get("regime", "chop")
        plt.axvspan(curr_idx, curr_idx + window_len, 
                    color=colors.get(regime, "gray"), alpha=0.2)
        curr_idx += window_len

    plt.title("Walk-Forward Performance with Regime Overlays")
    plt.show()