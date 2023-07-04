import pandas as pd
import numpy as np

class StockAnalyzer:
    def __init__(self):
        self.df = pd.read_csv(r"C:\Users\91635\Desktop\KukbitStock\kukbit\app\data\MarketData.csv")

    def preprocess_data(self):
        self.df['Date'] = pd.to_datetime('today').normalize()  # Set a common date for all records
        self.df = self.df.set_index('Date')

    def recommend_stocks(self, top_n):
        self.df['Score'] = self.df['Total Turnover(₹ Lac.)'] / self.df['No. of Shares Traded']
        self.df = self.df.sort_values(by='Score', ascending=False)
        top_stocks = self.df.head(top_n)
        security_names = top_stocks['Security Name'].tolist()
        return security_names

    
    
