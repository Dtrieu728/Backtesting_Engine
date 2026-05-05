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

    plt.figure()

    for i, r in enumerate(results):

        equity_dict = r["equity"]

        if strategy_name not in equity_dict:
            continue

        curve = np.array(equity_dict[strategy_name], dtype=float)

        plt.plot(curve, label=f"window {i}")

    plt.title(f"Equity Curve - {strategy_name}")
    plt.legend()
    plt.ylabel("Equity")
    plt.xlabel("Equity")
    plt.show()
    
def plot_turnover(results, strategy_name):

    plt.figure()

    for i, r in enumerate(results):

        turnover_dict = r["turnover"]

        if strategy_name not in turnover_dict:
            continue

        turnover = np.asarray(turnover_dict[strategy_name], dtype=float)

        plt.plot(turnover, alpha=0.6, label=f"window {i+1}")

    plt.title(f"Turnover ({strategy_name})")
    plt.ylabel("Turnover")
    plt.xlabel("Time")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    
def performance_summary(results_dict):
    summary = []
    
    for name,curve in results_dict.items():
        returns = np.diff(curve) / curve[:-1]
        sharpe = np.mean(returns)/np.std(returns) if np.std(returns) != 0 else 0
        max_dd= (max(curve) -min(curve))/max(curve)
        
        summary.append([name,sharpe,max_dd])
    
    return pd.DataFrame(summary, columns=["Strategy","Sharpe Ratio","Max Drawdown"])

def plot_portofolio_value(results,strategy_name):
    plt.figure()
    
    for i, r in enumerate(results):
        portfolio_value 

    