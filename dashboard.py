import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")

st.title("🤖 Crypto Trading Bot Dashboard")
st.markdown("Live monitoring interface for your Binance technical analysis strategy.")

# Initialize exchange
@st.cache_resource
def get_exchange():
    return ccxt.binance({'enableRateLimit': True})

exchange = get_exchange()

# Sidebar controls
st.sidebar.header("Bot Controls")
symbol = st.sidebar.selectbox("Trading Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT"], index=0)
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h"], index=2)
limit = st.sidebar.slider("Historical Candles", min_value=100, max_value=500, value=300, step=50)

if st.sidebar.button("Fetch Live Data & Analyze"):
    with st.spinner("Fetching data from Binance..."):
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Indicators
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['sma_50'] = ta.sma(df['close'], length=50)
        df['sma_200'] = ta.sma(df['close'], length=200)

        latest_close = df['close'].iloc[-1]
        latest_rsi = df['rsi'].iloc[-1]
        sma_50 = df['sma_50'].iloc[-1]
        sma_200 = df['sma_200'].iloc[-1]

        # Metrics layout
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${latest_close:,.2f}")
        col2.metric("14 RSI", f"{latest_rsi:.2f}")
        col3.metric("50 SMA", f"${sma_50:,.2f}" if not pd.isna(sma_50) else "N/A")
        col4.metric("200 SMA", f"${sma_200:,.2f}" if not pd.isna(sma_200) else "N/A")

        # Signal Logic display
        st.subheader("Current Market Signal")
        if not pd.isna(sma_200) and latest_rsi < 30 and latest_close > sma_200:
            st.success("STRONG BUY: Oversold asset in an overall uptrend.")
        elif latest_rsi < 30:
            st.warning("WEAK BUY: Oversold, but trading below 200 SMA.")
        elif not pd.isna(sma_200) and latest_rsi > 70 and latest_close < sma_200:
            st.error("STRONG SELL: Overbought asset in a downtrend.")
        elif latest_rsi > 70:
            st.warning("WEAK SELL: Overbought, but trading above 200 SMA.")
        else:
            st.info("NEUTRAL: No clear trading signal right now.")

        # Interactive Price Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name='Close Price', line=dict(color='orange')))
        if not pd.isna(sma_50):
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_50'], name='50 SMA', line=dict(color='blue', width=1)))
        if not pd.isna(sma_200):
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_200'], name='200 SMA', line=dict(color='purple', width=1)))
        
        fig.update_layout(title=f"{symbol} Price & Moving Averages", xaxis_title="Time", yaxis_title="Price (USDT)", height=500)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Click the **'Fetch Live Data & Analyze'** button in the sidebar to load your dashboard.")