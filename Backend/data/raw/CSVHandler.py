import yfinance as yf
user = input("Enter the symbol to download: ")
symbol = user.upper()
data = yf.download(symbol, start="2014-01-01", end="2024-01-01")
data.to_csv(f"{symbol}.csv")