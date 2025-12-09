import streamlit as st
from Stock_Functions import get_stock_data, stock_data_plot, volume_plot

st.set_page_config(layout="wide")
st.title("Mediocre Stock App")
st.subheader("By Ryland Perron")

# placeholder messages
temp_msg = st.empty()
temp_msg.write("Enter a stock ticker to get started!")

# sidebar header
st.sidebar.header("Stock Options")

# initialize session state
if 'last_fetched_ticker' not in st.session_state:
    st.session_state['last_fetched_ticker'] = "SPY"
if 'interval' not in st.session_state:
    st.session_state['interval'] = '1d'
if 'period' not in st.session_state:
    st.session_state['period'] = 'YTD'
if 'df_rel' not in st.session_state:
    st.session_state['df_rel'] = None
if 'df_max' not in st.session_state:
    st.session_state['df_max'] = None

# callback functions
def update_ticker():
    st.session_state['last_fetched_ticker'] = st.session_state['ticker_input'].upper()

def update_interval():
    new_interval = st.session_state['interval_input']
    st.session_state['interval'] = new_interval

    # Get valid options for the new interval
    options, default_value = interval_options.get(new_interval, (['1y','YTD','5y','10y','max'], 'YTD'))

    # If current period is not valid for new interval, reset to default
    if st.session_state['period'] not in options:
        st.session_state['period'] = default_value
  
def update_period():
    st.session_state['period'] = st.session_state['period_input']


# ticker input with callback
st.sidebar.text_input("Ticker:", value=st.session_state['last_fetched_ticker'], key='ticker_input', on_change=update_ticker).upper()

last_fetched_ticker = st.session_state['last_fetched_ticker']



# valid periods per interval
# this was cool to learn how to make 
interval_options = {
    '1m': (['1d','1wk'], '1d'),
    '1h': (['1d','1wk','1mo','3mo','6mo','1y','YTD','5y','10y','max'], '1d'),
    '1d': (['1wk','1mo','3mo','6mo','1y','YTD','5y','10y','max'], 'YTD'),
    '1wk': (['3mo','6mo','1y','YTD','5y','10y','max'], 'YTD'),
    '1mo': (['1y','YTD','5y','10y','max'], 'YTD'),
}

# interval selection with callback
st.sidebar.selectbox(
    "Interval:", ['1m','1h','1d','1wk','1mo'], index=['1m','1h','1d','1wk','1mo'].index(st.session_state['interval']), key='interval_input', on_change=update_interval)

# Get valid options for current interval
options, default_value = interval_options.get(st.session_state['interval'], (['1y','YTD','5y','10y','max'], 'YTD'))

# period selection with callback
st.sidebar.selectbox("Period:", options, index=options.index(st.session_state['period']), key='period_input', on_change=update_period)

# Use session state values directly
interval = st.session_state['interval']
period = st.session_state['period']


# loading message
load_msg = st.empty()
load_msg.write(f"Loading data for {last_fetched_ticker}, {interval}, {period}...")

# fetch data
try:
    df_rel, df_max, *_ = get_stock_data(symbol=last_fetched_ticker, period=period, interval=interval)
    if df_rel.empty:
        st.warning(f"No data found for ticker '{last_fetched_ticker}'. *Hint: tickers are often 3-5 capital letters with no space or numbers.")
        st.session_state.pop('df_rel', None)
        st.session_state.pop('df_max', None)
    else:
        st.session_state['df_rel'] = df_rel
        st.session_state['df_max'] = df_max
except Exception as e:
    st.error(f"An error occurred while fetching data: {e}")
    st.session_state.pop('df_rel', None)
    st.session_state.pop('df_max', None)

# clear messages
load_msg.empty()
temp_msg.empty()

# plotting
if 'df_rel' in st.session_state and not st.session_state['df_rel'].empty:
    fig_stock = stock_data_plot(st.session_state['df_rel'], title=last_fetched_ticker)
    fig_volume = volume_plot(st.session_state['df_rel'])
    st.pyplot(fig_stock)
    st.pyplot(fig_volume)


