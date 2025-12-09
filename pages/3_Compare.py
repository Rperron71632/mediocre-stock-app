import streamlit as st
from Stock_Functions import stock_compare

st.title("Stock Comparison")
st.sidebar.header("Comparison Options")

# Check if data exists
if 'df_rel' not in st.session_state or st.session_state['df_rel'] is None:
    st.warning("No stock data loaded. Please go to the main page and fetch data for a stock first.")
    st.stop()

if 'last_fetched_ticker' not in st.session_state:
    st.session_state['last_fetched_ticker'] = 'SPY'

if 'interval' not in st.session_state:
    st.session_state['interval'] = '1d'
if 'period' not in st.session_state:
    st.session_state['period'] = 'YTD'

# get the loaded stock info
main_ticker = st.session_state['last_fetched_ticker']
interval = st.session_state['interval']
period = st.session_state['period']
df_rel = st.session_state['df_rel']

# comparison ticker input
st.sidebar.subheader("Compare Against")
compare_ticker = st.sidebar.text_input("Comparison Ticker:", value="SPY",).upper()

st.sidebar.write(f"**Main Stock:** {main_ticker}")
st.sidebar.write(f"**Interval:** {interval}")
st.sidebar.write(f"**Period:** {period}")

# run comparison
if compare_ticker:
    try:
        with st.spinner(f"Comparing {main_ticker} vs {compare_ticker}..."):
            fig, df_pct, ret1, ret2, corr = stock_compare(
                df_1=df_rel,
                interval=interval,
                ticker_mem=st.session_state['last_fetched_ticker'],
                ticker_compare=compare_ticker
            )
        
        # Display the plot
        st.pyplot(fig)
        
        # Analysis section
        st.subheader("Performance Analysis")
        
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label=f"{main_ticker} Total Return", value=f"{ret1:.2f}%", delta=None)
        
        with col2:
            st.metric(label=f"{compare_ticker} Total Return", value=f"{ret2:.2f}%", delta=None)
        
        with col3:
            st.metric(label="Correlation", value=f"{corr:.3f}", delta=None)
        
        st.subheader("What This Means")
        
        # performance comparison
        outperformance = ret1 - ret2
        if abs(outperformance) < 1:
            perf_text = f"**{main_ticker}** and **{compare_ticker}** performed nearly identically, with a difference of only {abs(outperformance):.2f}%."
        elif outperformance > 0:
            perf_text = f"**{main_ticker}** outperformed **{compare_ticker}** by **{outperformance:.2f}%** during this period."
        else:
            perf_text = f"**{compare_ticker}** outperformed **{main_ticker}** by **{abs(outperformance):.2f}%** during this period."
        
        st.write(perf_text)
        
        # correlation interpretation
        if corr > 0.7:
            corr_text = f"The stocks show **strong positive correlation** ({corr:.3f}), meaning they tend to move together. This suggests similar market drivers or sector exposure."
        elif corr > 0.3:
            corr_text = f"The stocks show **moderate positive correlation** ({corr:.3f}), meaning they sometimes move together but maintain some independence."
        elif corr > -0.3:
            corr_text = f"The stocks show **weak correlation** ({corr:.3f}), meaning they move relatively independently of each other."
        elif corr > -0.7:
            corr_text = f"The stocks show **moderate negative correlation** ({corr:.3f}), meaning they often move in opposite directions."
        else:
            corr_text = f"The stocks show **strong negative correlation** ({corr:.3f}), meaning they tend to move in opposite directions. This could indicate a hedging relationship."
        
        st.write(corr_text)
        
        # risk/diversification insight
        st.subheader("Investment Insight")
        if corr < 0.5:
            st.success(f"These stocks could provide **good diversification** in a portfolio due to their low correlation ({corr:.3f}).")
        else:
            st.info(f"These stocks tend to move together (correlation: {corr:.3f}), so they may not provide significant diversification benefits.")
        
    except Exception as e:
        st.error(f"Error comparing stocks")
        st.warning(f"No data found for ticker '{compare_ticker}'. *Hint: tickers are often 3-5 capital letters with no space or numbers.")