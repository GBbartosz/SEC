import yfinance as yf

# Ticker symbol of the stock
ticker_symbol = 'NVDA'  # Example: Apple Inc.

# Download shares outstanding data
stock_info = yf.Ticker(ticker_symbol)
shares_outstanding = stock_info.info.get('sharesOutstanding')
print(shares_outstanding)
