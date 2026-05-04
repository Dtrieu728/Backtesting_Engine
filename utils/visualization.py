import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os 


current_dir = os.path.dirname(os.path.abspath(__file__))

def plot_equity_curves(results_dict):
    os.makedirs(os.path.join(current_dir, "plots"), exist_ok=True)
    os.chdir(os.path.join(current_dir, "plots"))
    
    
    plt.figure(figsize=(12,6))

    for name, curve in results_dict.items():
        plt.plot(curve, label=name)
    
    plt.xlabel("Time")
    plt.ylabel("Normalized Equity")
    plt.title("Strategy Performance Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(current_dir, "plots", "equity_curves.png"))
    plt.show()
    
def plot_equity(results, strategy_name):
    full_curve = []

    for r in results:
        equity = r["equity"][strategy_name]
        full_curve.extend(equity)

    plt.figure()
    plt.plot(full_curve)
    plt.title("Walk-Forward Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.savefig(os.path.join(current_dir, "plots","equity_plot.png"))


def plot_turnover(results, strategy_name):
    turnover = []

    for r in results:
        turnover.extend(r["turnover"][strategy_name])

    plt.figure()
    plt.plot(turnover)
    plt.title("Turnover Over Time")
    plt.xlabel("Time")
    plt.ylabel("Turnover")
    plt.savefig(os.path.join(current_dir, "plots","turnOver_plot.png"))
    
def performance_summary(results_dict):
    summary = []
    
    for name,curve in results_dict.items():
        returns = np.diff(curve) / curve[:-1]
        sharpe = np.mean(returns)/np.std(returns) if np.std(returns) != 0 else 0
        max_dd= (max(curve) -min(curve))/max(curve)
        
        summary.append([name,sharpe,max_dd])
    
    return pd.DataFrame(summary, columns=["Strategy","Sharpe Ratio","Max Drawdown"])