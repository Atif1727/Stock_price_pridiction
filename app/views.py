from urllib import request
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from plotly.graph_objs import Scatter

import pandas as pd
import numpy as np
import json

import yfinance as yf
import datetime as dt

from .models import Project
from .Stocks import StockAnalyzer
# Create your views here.

# for stock_code, predicted_prices in predictions.items():
#     print(f"Stock Code: {stock_code}")
#     print(f"Predicted Prices: {predicted_prices}")
#     print()

# The Home page when Server loads up
def index(request):
    stock_analyzer = StockAnalyzer()
    top_stocks= stock_analyzer.recommend_stocks(6)
    # top_stocks = list(top_stocks)
    tickers=[]
    for stock in top_stocks:
        ticker_with_suffix = f"{stock}.NS"  # Append '.NS' to the stock ticker
        tickers.append(ticker_with_suffix)  # Append the modified ticker to the list
        print(stock)
 

    data = yf.download(
        
        # passes the ticker
        tickers=tickers,
        
        group_by = 'ticker',
        
        threads=True, # Set thread value to true
        
        # used for access data[ticker]
        period='1mo', 
        interval='1d'
    
    )

    data.reset_index(level=0, inplace=True)
    fig_left = go.Figure()
    for ticker in tickers:
        try:
            fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data[ticker]['Adj Close'], name=ticker))
        except Exception as e:
            print(f"{ticker}: {e}")
            continue
    
    fig_left.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")

    plot_div_left = plot(fig_left, auto_open=False, output_type='div')

    dfs = []

    for ticker in tickers:
        try:
            df = yf.download(tickers=ticker, period='1m', interval='1d')
            df.insert(0, "Ticker", ticker)
            dfs.append(df)
        except Exception as e:
            print(f"{ticker}: {e}")

    if dfs:
        df = pd.concat(dfs, axis=0)
        df.reset_index(level=0, inplace=True)
        df.columns = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume']
        df['Date'] = df['Date'].astype(str)
        df.drop('Date', axis=1, inplace=True)

        json_records = df.to_json(orient='records')
        recent_stocks = json.loads(json_records)
    else:
        recent_stocks = []

    # ========================================== Page Render section =====================================================

    return render(request, 'index.html', {
        'plot_div_left': plot_div_left,
        'recent_stocks': recent_stocks
    })


def ticker(request):
    return render(request, 'ticker.html')

def search(request):
    return render(request, 'search.html')