import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os 

def plot_equity_curves(results_dict):
    current_dir = os.path.dirname(os.path.abspath(__file__))
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
    
def performance_summary(results_dict):
    summary = []
    
    for name,curve in results_dict.items():
        returns = np.diff(curve) / curve[:-1]
        sharpe = np.mean(returns)/np.std(returns) if np.std(returns) != 0 else 0
        max_dd= (max(curve) -min(curve))/max(curve)
        
        summary.append([name,sharpe,max_dd])
    
    return pd.DataFrame(summary, columns=["Strategy","Sharpe Ratio","Max Drawdown"])