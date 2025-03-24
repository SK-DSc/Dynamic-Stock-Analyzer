import pandas as pd
import yfinance as yf
from yahooquery import Ticker
import requests

def fetch_stock_data(stock_symbol, period='1y'):
    """Fetch historical stock data from Yahoo Finance."""
    stock = yf.Ticker(stock_symbol)
    return stock.history(period=period)

def fetch_financial_metrics(stock_symbol):
    """Fetch key financial metrics using yahooquery."""
    ticker = Ticker(stock_symbol)
    return ticker.key_stats[stock_symbol]
