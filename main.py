import yfinance as yf
import os, requests, threading, time
from flask import Flask
import numpy as np

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TIMEFRAMES = ["5m", "15m"]

def send_tg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

def find_pivots(data, window=5):
    highs, lows = [], []
    for i in range(window, len(data)-window):
        if data[i] == max(data[i-window:i+window+1]):
            highs.append((i, data[i]))
        if data[i] == min(data[i-window:i+window+1]):
            lows.append((i, data[i]))
    return highs, lows

def check_pattern(tf):
    try:
        period = "7d" if tf == "5m" else "10d"
        df = yf.download("EURUSD=X", period=period, interval=tf, progress=False)
        if len(df) < 100: return
        closes = df['Close'].values
        price = float(closes[-1])

        # Detecta últimos 5 pivots para armar XABCD
        highs, lows = find_pivots(closes)
        pivots = sorted(highs + lows)
        if len(pivots) < 5: return
        X,A,B,C,D = [p[1] for p in pivots[-5:]]

        # Cálculo simple de ratios con tu config
        XA = abs(A-X)
        AB = abs(B-A)
        BC = abs(C-B)
        CD = abs(D-C)
        AD = abs(D-A)

        # GARTLEY: XB 61.8% - AD 78.6%
        is_gartley = abs((AB/XA) - 0.618) < 0.08 and abs((AD/XA) - 0.786) < 0.08
        # BUTTERFLY: XB 78.6% - AD 1.27
        is_butterfly = abs((AB/XA) - 0.786) < 0.08 and abs((AD/XA) - 1.27) < 0.15
        # CYPHER: XB 38-61% - AD 78.6%
        is_cypher = (0.382 <= AB/XA <= 0.618) and abs((AD/XA) - 0.786) < 0.08

        # === TU TP SOLO PUNTO C ===
        tp_c = float(C) # <-- TP = punto C exacto

        if is_gartley:
            send_tg(f"🔷 GARTLEY {tf} EURUSD\nEntrada D: {D:.5f}\nTP Unico en C: {tp_c:.5f}\nPrecio actual: {price:.5f}")
        if is_butterfly:
            send_tg(f"🦋 BUTTERFLY {tf} EURUSD\nEntrada D: {D:.5f}\nTP Unico en C: {tp_c:.5f}\nPrecio actual: {price:.5f}")
        if is_cypher:
            send_tg(f"🔶 CYPHER {tf} EURUSD\nEntrada D: {D:.5f}\nTP Unico en C: {tp_c:.5f}\nPrecio actual: {price:.5f}")

        print(f"Scan {tf} OK - TP C = {tp_c:.5f}")

    except Exception as e:
        print(f"Error {tf}: {e}")

def scan_all():
    for tf in TIMEFRAMES:
        check_pattern(tf)

@app.route("/")
def home():
    return "Bot ACTIVO: Gartley/Butterfly/Cypher - TP Unico C - 5m y 15m FOREXCOM"

@app.route("/test")
def test():
    send_tg("✅ PRUEBA: Gartley/Butterfly/Cypher EURUSD 5m y 15m - TP en punto C (como pediste)")
    return "Prueba enviada"

@app.route("/scan")
def scan():
    scan_all()
    return "Scan 5m y 15m hecho"

def loop():
    while True:
        scan_all()
        time.sleep(300)

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
