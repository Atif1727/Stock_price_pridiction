from urllib import request
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.core.cache import cache

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
from .stocks import StockAnalyzer
from .stockPredictor import StockPredictor


def index(request):
    # Check if the cached data exists
    cached_data = cache.get('stock_data')

    if cached_data:
        # If cached data exists, retrieve it from the cache
        data = cached_data['data']
        tickers = cached_data['tickers']
    else:
        # If cached data doesn't exist, download the data and store it in the cache
        stock_analyzer = StockAnalyzer()
        top_stocks = stock_analyzer.recommend_stocks(6)

        tickers = []
        for stock in top_stocks:
            ticker_with_suffix = f"{stock}.NS"  # Append '.NS' to the stock ticker
            tickers.append(ticker_with_suffix)  # Append the modified ticker to the list

        data = yf.download(
            tickers=tickers,
            group_by='ticker',
            threads=True,
            period='1mo',
            interval='1d'
        )

        # Store the data and tickers in the cache for 5 minutes
        cache.set('stock_data', {'data': data, 'tickers': tickers}, 300)

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


    return render(request, 'index.html', {
        'plot_div_left': plot_div_left,
        'recent_stocks': recent_stocks
    })



def ticker(request):

    ticker_df = pd.read_csv('app/data/new_tickers.csv') 
    json_ticker = ticker_df.reset_index().to_json(orient ='records')
    ticker_list = []
    ticker_list = json.loads(json_ticker)


    return render(request, 'ticker.html', {
        'ticker_list': ticker_list
    })

def search(request):
    return render(request, 'search.html', {})


def predict(request, ticker_value, number_of_days):
    try:
        ticker_value = ticker_value.upper()
        df = yf.download(tickers = ticker_value, period='1d', interval='1m')
        print("Downloaded ticker = {} successfully".format(ticker_value))
    except:
        return render(request, 'API_Down.html', {})

    try:
        # number_of_days = request.POST.get('days')
        number_of_days = int(number_of_days)
    except:
        return render(request, 'Invalid_Days_Format.html', {})
    
    if number_of_days < 0:
        return render(request, 'Negative_Days.html', {})
    
    if number_of_days > 365:
        return render(request, 'Overflow_days.html', {})
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'], name = 'market data'))
    fig.update_layout(
                        title='{} live share price evolution'.format(ticker_value),
                        yaxis_title='Stock Price (USD per Shares)')
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=15, label="15m", step="minute", stepmode="backward"),
            dict(count=45, label="45m", step="minute", stepmode="backward"),
            dict(count=1, label="HTD", step="hour", stepmode="todate"),
            dict(count=3, label="3h", step="hour", stepmode="backward"),
            dict(step="all")
        ])
        )
    )
    fig.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")
    plot_div = plot(fig, auto_open=False, output_type='div')


    #machine learning
    ticker =ticker_value  # Ticker for NSE  Sensex Index
    n_days = number_of_days

    stock_predictor = StockPredictor(ticker)
    stock_predictor.load_data()
    stock_predictor.train_model(p=5, d=1, q=0)  # Specify the order of the ARIMA model
    forecast = stock_predictor.predict(n_days)

    pred_dict = {"Date": [], "Prediction": []}
    for i in range(0, len(forecast)):
        pred_dict["Date"].append(dt.datetime.today() + dt.timedelta(days=i))
        pred_dict["Prediction"].append(forecast[i])
    
    pred_df = pd.DataFrame(pred_dict)
    pred_fig = go.Figure([go.Scatter(x=pred_df['Date'], y=pred_df['Prediction'])])
    pred_fig.update_xaxes(rangeslider_visible=True)
    pred_fig.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")
    plot_div_pred = plot(pred_fig, auto_open=False, output_type='div')


    stock_data = yf.Ticker(ticker)

    # Get the stock info
    stock_info = stock_data.info

    # Extract the required information
    symbol = stock_info['symbol']
    name = stock_info['longName']
    market_cap = stock_info['marketCap']
    country = stock_info['country']
    volume = stock_info['regularMarketVolume']
    sector = stock_info['sector']
    industry = stock_info['industry']


    return render(request, "result.html", context={ 'plot_div': plot_div, 
                                                    'confidence' : "",
                                                    'forecast': forecast,
                                                    'ticker_value':ticker_value,
                                                    'number_of_days':number_of_days,
                                                    'plot_div_pred':plot_div_pred,
                                                    'Symbol':symbol,
                                                    'Name':name,
                                                    'Market_Cap':market_cap,
                                                    'Country':country,
                                                    'Volume':volume,
                                                    'Sector':sector,
                                                    'Industry':industry,
                                                    })