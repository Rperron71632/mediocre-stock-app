import streamlit as st
from Stock_Functions import annual_performance, historical_volatility 


st.set_page_config(layout="wide")
st.title("Performance & Volatility")
st.sidebar.header("Stock Options")

# ensure ticker exists
# if 'last_fetched_ticker' not in st.session_state:
#     st.session_state['last_fetched_ticker'] = 'AAPL'

# Define the variable from session state
last_fetched_ticker = st.session_state['last_fetched_ticker']

# Display the ticker (read-only) so user can see what's loaded
st.sidebar.text_input(
    "Current Ticker:",
    value=last_fetched_ticker,
    disabled=True  # Make it read-only
)

# volatility slider
if 'vol_window' not in st.session_state:
    st.session_state['vol_window'] = 30

vol_window = st.sidebar.slider(
    "Volatility window (days):",
    min_value=2,
    max_value=252,
    key='vol_window'
)

st.sidebar.write(f"Data for Ticker: **{last_fetched_ticker}**")

# check if data is ready
data_is_ready = ('df_max' in st.session_state and 'df_rel' in st.session_state)

if not data_is_ready:
    st.warning(f"No data loaded for ticker **{last_fetched_ticker}**. Please go to the main page to fetch data.")
else:
    df_rel = st.session_state['df_rel']
    df_max = st.session_state['df_max']

    st.write(f"**Current Ticker:** {last_fetched_ticker}")
    st.write(f"**Volatility Window:** {vol_window} days")

    # annual performance
    st.subheader("Annual Performance")
    try:
        if df_max.empty:
            st.warning("Not enough data to calculate annual performance.")
        else:
            fig_perf, performance_results = annual_performance(df_max)
            st.pyplot(fig_perf)
    except Exception as e:
        st.error(f"Error calculating annual performance: {e}")

    # historical volatility
    st.subheader("Historical Volatility")
    try:
        if df_max.empty or len(df_max) < vol_window:
            st.warning(f"Not enough data for a {vol_window}-day window.")
        else:
            fig_vol, hv_series = historical_volatility(df_max, window=vol_window)
            st.pyplot(fig_vol)
    except Exception as e:
        st.error(f"Error calculating historical volatility: {e}")
