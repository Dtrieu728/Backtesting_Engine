import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_equity_curves(results_dict):
    plt.figure(figsize=(12,6))

    for name, curve in results_dict.items():
        plt.plot(curve, label=name)
    
    plt.xlabel("Time Steps(Days)")
    plt.ylabel("Equity Value ($)")
    plt.title("Strategy Performance Comparison")
    plt.legend()
    plt.show()
    
def performance_summary(results_dict):
    summary = []
    
    for name,curve in results_dict.items():
        returns = np.diff(curve) / curve[:-1]
        sharpe = np.mean(returns)/np.std(returns) if np.std(returns) != 0 else 0
        max_dd= (max(curve) -min(curve))/max(curve)
        
        summary.append([name,sharpe,max_dd])
    
    return pd.DataFrame(summary, columns=["Strategy","Sharpe Ratio","Max Drawdown"])