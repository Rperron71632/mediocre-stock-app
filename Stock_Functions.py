import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.ticker import FuncFormatter 
import yfinance as yf

@st.cache_data
def get_stock_data(symbol: str, period: str = 'max', interval: str = '1mo'):
    """
    Fetches and caches stock data from Yahoo Finance based on a period and interval.

    Returns:
    (df_rel, df_max, stock_info, standerd_dev, varr)
    """


    period_for_fetch = period
    stock = yf.Ticker(symbol)

    # Fetch the data specific to the user's selected period/interval (df_rel)
    df_rel = stock.history(period=period_for_fetch, interval=interval)
    
    # fetch the max history, always daily ('1d') for annual performance (df_max)
    df_max = stock.history(period='max', interval='1d')
    
    # fetch stock data
    stock_info = stock.info

    
    if df_rel.empty:
        # if no data is found
        return pd.DataFrame(), pd.DataFrame(), {}, 0.0, 0.0

    standerd_dev = np.std(df_rel['Close']) 
    varr = standerd_dev**2

    return df_rel, df_max, stock_info, standerd_dev, varr
    

def stock_data_plot(df_rel,title: str,mav: list=[],line_type: str='candle'):
    '''
    this is the main plotting fucntion using the mplfinance library. 
    imputs: 
    pandas DataFrame 
    moving average(s) values 
    line type which deafults to candles 

    '''

    if len(mav) == 0:
        fig, axlist = mpf.plot(df_rel, type=line_type, style='yahoo', figratio=(12,6), figscale=1.5, returnfig=True)
        axlist[0].set_title(title, fontsize=25)
        axlist[0].set_xlabel('Date', fontsize=10)
        axlist[0].set_ylabel('Price($)', fontsize=10)
        for label in axlist[0].get_xticklabels():
            label.set_fontsize(10)
        for label in axlist[0].get_yticklabels():
            label.set_fontsize(10)

    else: # didn't end up allowing the user to add moving averages. maybe they should use a real stock app if they want those features lol. 
        fig, axlist = mpf.plot(df_rel, mav=mav, type=line_type, style='yahoo', figratio=(50,15), figscale=6, returnfig=True)
        axlist[0].set_title(title, fontsize=60)
        axlist[0].set_xlabel('Date', fontsize=35)
        axlist[0].set_ylabel('Price($)', fontsize=35)
        for label in axlist[0].get_xticklabels():
            label.set_fontsize(30)
        for label in axlist[0].get_yticklabels():
            label.set_fontsize(30)

    return fig



def volume_plot(df_rel):

    '''
    this is the general volume plotting fucntion. 

    inputs:
    df_rel 

    outputs: 
    volume graph with: 
    - green bars for days in which the buy volume was greater than the sell volume. 
    - red bars for days in which the sell volume was greater than the buy volume. 

    '''


    colors = ['green' if c >= o else 'red' for c, o in zip(df_rel['Close'], df_rel['Open'])]
    x = np.arange(len(df_rel))

    fig, ax = plt.subplots(figsize=(18,6))
    ax.bar(x, df_rel['Volume'], color=colors, width=1.0, align='edge')  # align bars to left
    ax.set_xlim(0, len(df_rel))  # x-axis starts at 0

    ax.set_title("Historical Volume", fontsize=30)
    ax.set_xlabel("Date", fontsize=20)
    ax.set_ylabel("Volume", fontsize=20)

    # X-axis labels
    xticks = np.arange(0, len(df_rel), max(len(df_rel)//10, 1))
    xlabels = [df_rel.index[i].strftime('%Y-%b-%d') for i in xticks]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, rotation=55, fontsize=15)

    # Y-axis formatter
    def ytick(x, _):
        if x >= 1_000_000_000:
            return f"{x/1_000_000_000:.1f}B"
        elif x >= 1_000_000:
            return f"{x/1_000_000:.1f}M"
        elif x >= 1_000:
            return f"{x/1_000:.1f}k"
        else:
            return str(int(x))
    ax.yaxis.set_major_formatter(FuncFormatter(ytick))

    plt.tight_layout()
    return fig




def annual_performance(df):
    '''
    calculates yearly preformace of a security and plots it. upward green bars are % gain in a year while downward red bars are % loss in a year.

    inputs:
    Pandas dataframe imported from Yfinance on the '1d' timeframe 
    
    
    '''
    df = df.copy()
    df["Year"] = df.index.year
    results = {}

    for year, group in df.groupby("Year"):
        group = group.sort_index()

        # skip years with too few data points
        if len(group) < 30:
            continue

        start_price = group['Close'].iloc[0]
        end_price = group['Close'].iloc[-1]

        n_days = len(group)
        total_return = end_price / start_price

        # annualize if less than a full year
        if n_days >= 360:
            annualized = total_return - 1
        else:
            annualized = (total_return ** (365 / n_days)) - 1

        results[year] = annualized * 100

    years = list(results.keys())
    returns = list(results.values())
    colors = ['green' if r >= 0 else 'red' for r in returns]

    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(years, returns, color=colors)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual Return (%)")
    ax.set_title("Annual Stock Returns")

    return fig, results



def historical_volatility(df_max, window=30, trading_days=252):
    """
    Calculate rolling historical volatility and optionally plot it.

    inputs:
    df: pandas DataFrame with 1d interval  
    window : rolling window size (in days). defualts to 30 days
    trading_days : annualization factor. defaults to 252. Prob will not let the user change it. 

    Returns:
    hv_series : Pandas Series of rolling annualized vol

    creates a line chart of historical volatility  
    """


    df_max = df_max.copy()
    df_max['log_return'] = np.log(df_max['Close'] / df_max['Close'].shift(1))
    rolling_daily_vol = df_max['log_return'].rolling(window).std()
    hv_series = rolling_daily_vol * np.sqrt(trading_days)
    hv_series = hv_series.dropna() 

    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(hv_series.index, hv_series, label=f"{window}-Day Historical Volatility")
    ax.set_ylabel("Volatility (Annualized)")
    ax.set_title(f"{window}-Day Historical Volatility")
    ax.axhline(hv_series.iloc[-1], color='red', linestyle='--', linewidth=0.8, label=f"Latest HV: {hv_series.iloc[-1]:.2%}")
    ax.legend()
    ax.grid(True)

    return fig, hv_series



def stock_compare(df_1, interval, ticker_mem, ticker_compare="SPY"):
    '''
    Compares a user-provided stock DataFrame (df_1) to another stock (default SPY)
    using the same interval the user originally fetched 

    df_1: stock dataframe already in memory
    interval: interval used to fetch df_1 ("1d", "1wk", "1mo", etc)
    ticker_mem: the ticker symbol for df_1 (for labeling)
    ticker_compare: baseline ticker to compare against
    '''

    df_compare, _, _, _, _ = get_stock_data(ticker_compare, interval=interval)

    # ensure alignment - use ticker_mem instead of "Stock1"
    df_combined = pd.DataFrame({ticker_mem: df_1["Close"], ticker_compare: df_compare["Close"]}).dropna()

    # normalize
    df_norm = df_combined / df_combined.iloc[0]

    # convert to %
    df_pct = (df_norm - 1) * 100

    # plot - use ticker_mem for labels
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_pct.index, df_pct[ticker_mem], label=ticker_mem, linewidth=2)
    ax.plot(df_pct.index, df_pct[ticker_compare], label=ticker_compare, linewidth=2)

    # format y-axis as %
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}%'))

    # move y-axis to the right
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()

    ax.set_title(f"Percent Return Comparison ({interval} interval)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Return")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()

    # Metrics - use ticker_mem
    ret1 = df_pct[ticker_mem].iloc[-1]
    ret2 = df_pct[ticker_compare].iloc[-1]
    corr = df_combined[ticker_mem].corr(df_combined[ticker_compare])

    return fig, df_pct, ret1, ret2, corr
