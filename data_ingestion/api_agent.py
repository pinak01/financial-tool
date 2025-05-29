import yfinance as yf
import pandas as pd

class MarketDataAgent:
    def fetch_stock_data(self, symbols, start_date, end_date):
        # Fetch stock data
        data = yf.download(symbols, start=start_date, end=end_date)
        return data
    
    def get_earnings_data(self, symbol):
        # Fetch earnings data
        stock = yf.Ticker(symbol)
        earnings = stock.earnings
        return earnings