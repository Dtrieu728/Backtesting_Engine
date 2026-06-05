import pandas as pd
import matplotlib.pyplot as plt
import json

# load C++ trade log
trades = pd.read_csv("trades.csv", parse_dates=["timestamp"])
prices = pd.read_csv("prices.csv", parse_dates=["timestamp"])

# load session summary
with open("session_summary.json") as f:
    summary = json.load(f)

# reconstruct equity curve from trades
initial_capital = 10000.0
cash = initial_capital
holdings = 0
equity = []

for _, price_row in prices.iterrows():
    price = price_row["price"]
    ts    = price_row["timestamp"]

    # apply any trades at this timestamp
    matching = trades[trades["timestamp"] == ts]
    for _, trade in matching.iterrows():
        qty = trade["quantity"]
        cash -= qty * trade["price"]
        holdings += qty

    equity.append({
        "timestamp": ts,
        "equity": cash + holdings * price
    })

eq_df = pd.DataFrame(equity).set_index("timestamp")

# plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

prices.set_index("timestamp")["price"].plot(
    ax=ax1, color="dodgerblue", label="Price")
ax1.set_title(f"C++ Simulator Session — {summary['strategy']}")
ax1.set_ylabel("Price ($)")
ax1.legend()

eq_df["equity"].plot(
    ax=ax2, color="green", label="Equity")
ax2.axhline(initial_capital, color="grey",
            linestyle="--", label="Starting capital")
ax2.set_ylabel("Portfolio Value ($)")
ax2.set_xlabel("Time")
ax2.legend()

plt.tight_layout()
plt.savefig("session_equity.png")
plt.show()

print(f"\nStrategy:     {summary['strategy']}")
print(f"Final cash:   ${summary['final_cash']:.2f}")
print(f"Holdings:     {summary['holdings']} units")
print(f"Total ticks:  {summary['total_ticks']}")