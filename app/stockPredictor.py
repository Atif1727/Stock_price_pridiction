import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA

class StockPredictor:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None

    def load_data(self):
        stock_data = yf.download(self.ticker, period='10y')
        self.data = stock_data[['Close']].values

    def train_model(self, p, d, q):
        model = ARIMA(self.data, order=(p, d, q))
        self.model = model.fit()

    def predict(self, n_days):
        forecast = self.model.forecast(steps=n_days)
        return forecast


