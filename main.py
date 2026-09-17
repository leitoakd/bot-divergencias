import time
import yfinance as yf

print("Bot iniciado...")

while True:
    try:
        df = yf.download("GBPUSD=X", period="1d", interval="15m")
        precio = df['Close'].iloc[-1]
        print(f"GBPUSD: {precio}")
    except Exception as e:
        print(e)
    time.sleep(60)
