import ccxt
import pandas as pd
import pandas_ta as ta
import time

# Initialize public exchange connection
exchange = ccxt.binance({
    'enableRateLimit': True,
})

def run_bot(symbol='BTC/USDT', timeframe='15m', limit=100):
    print(f"\n[{pd.Timestamp.now()}] Fetching market data for {symbol}...")
    try:
        # Fetch OHLCV candles
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Calculate Indicators (RSI and Simple Moving Averages)
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['sma_50'] = ta.sma(df['close'], length=50)
        df['sma_200'] = ta.sma(df['close'], length=200)

        # Get latest metrics
        latest_close = df['close'].iloc[-1]
        latest_rsi = df['rsi'].iloc[-1]
        sma_50 = df['sma_50'].iloc[-1]
        sma_200 = df['sma_200'].iloc[-1]

        print(f"Current BTC Price: ${latest_close:,.2f}")
        print(f"14-period RSI:     {latest_rsi:.2f}")
        print(f"50-period SMA:     ${sma_50:,.2f}")
        print(f"200-period SMA:    ${sma_200:,.2f}")

        # Strategy Logic with Trend Confirmation
        if latest_rsi < 30 and latest_close > sma_200:
            print(">>> Signal: STRONG BUY (Oversold in an overall uptrend)")
        elif latest_rsi < 30:
            print(">>> Signal: WEAK BUY / CAUTION (Oversold, but below 200 SMA downtrend)")
        elif latest_rsi > 70 and latest_close < sma_200:
            print(">>> Signal: STRONG SELL (Overbought in a downtrend)")
        elif latest_rsi > 70:
            print(">>> Signal: WEAK SELL / CAUTION (Overbought, but above 200 SMA uptrend)")
        else:
            print(">>> Signal: Neutral (No action)")

    except Exception as e:
        print(f"Error fetching data: {e}")

# Continuous loop running every 15 minutes (900 seconds)
print("Starting Crypto Trading Bot Loop. Press Ctrl+C to stop.")
while True:
    run_bot()
    print("Waiting 15 minutes for the next candle...")
    time.sleep(900)