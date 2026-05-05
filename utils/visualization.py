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
    
def plot_equity(results):
    full_curve = []

    for i, r in enumerate(results):
        strat = r["strategy"]
        equity = np.array(r["equity"][strat])

        # normalize each window to start at 1
        equity = equity / equity[0]

        if len(full_curve) == 0:
            full_curve.extend(equity)
        else:
            # stitch smoothly
            last_val = full_curve[-1]
            full_curve.extend(equity * last_val)

    plt.figure(figsize=(10,5))
    plt.plot(full_curve)
    plt.title("Walk-Forward Equity Curve (Strategy Switching)")
    plt.xlabel("Time")
    plt.ylabel("Equity")

    plt.savefig(os.path.join(current_dir, "plots", "equity_plot.png"))
    plt.show()


def plot_turnover(results):
    full_turnover = []

    for r in results:
        strat = r["strategy"]  
        turnover = r["turnover"][strat]

        full_turnover.extend(turnover)

    plt.figure(figsize=(10,5))
    plt.plot(full_turnover)
    plt.title("Turnover Over Time (Strategy Switching)")
    plt.xlabel("Time")
    plt.ylabel("Turnover")

    plt.savefig(os.path.join(current_dir, "plots", "turnover_plot.png"))
    plt.show()
    
def performance_summary(results_dict):
    summary = []
    
    for name,curve in results_dict.items():
        returns = np.diff(curve) / curve[:-1]
        sharpe = np.mean(returns)/np.std(returns) if np.std(returns) != 0 else 0
        max_dd= (max(curve) -min(curve))/max(curve)
        
        summary.append([name,sharpe,max_dd])
    
    return pd.DataFrame(summary, columns=["Strategy","Sharpe Ratio","Max Drawdown"])