import yfinance as yf

data = yf.download("META", start="2014-01-01", end="2024-01-01")
data.to_csv("META.csv")