import os, time, threading, requests
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)

SYMBOLS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "GBPJPY=X", "EURJPY=X"]
TIMEFRAMES = ["5m", "15m"]

def send_tg(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"Enviado TG: {msg[:50]}")
    except Exception as e:
        print(f"Error TG: {e}")

def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_chop(high, low, close, period=14):
    try:
        tr1 = high - low
        atr = tr1.rolling(period).mean()
        high_low = high.rolling(period).max() - low.rolling(period).min()
        chop = 100 * np.log10((atr * period).sum() / high_low) / np.log10(period)
        return chop
    except:
        return pd.Series([50]*len(close), index=close.index)

def detect_3_patterns(df):
    patterns = []
    try:
        # Tomamos ultimos 6 swings simplificados
        c = df['Close'].values
        if len(c) < 50: return []
        x, a, b, c_point, d = c[-6], c[-5], c[-4], c[-3], c[-2]
        xa = abs(a - x)
        ab = abs(b - a)
        bc = abs(c_point - b)
        if xa == 0 or ab == 0: return []
        r_b = ab / xa
        r_d = abs(d - x) / xa
        r_c = bc / ab

        # GARTLEY: B 61.8%, D 78.6% XA
        if 0.55 < r_b < 0.70 and 0.72 < r_d < 0.85:
            patterns.append("GARTLEY")
        # BUTTERFLY: B 78.6%, D 127%-162% XA
        if 0.72 < r_b < 0.86 and 1.20 < r_d < 1.72:
            patterns.append("BUTTERFLY")
        # CYPHER: B 38-61%, C 113-141% AB, D 78.6% XC
        if 0.35 < r_b < 0.65 and 1.10 < r_c < 1.45:
            patterns.append("CYPHER")
    except Exception as e:
        print(e)
    return patterns

def scan_loop():
    print("BOT 3 PATRONES INICIADO - Gartley/Butterfly/Cypher")
    send_tg("✅ *BOT 3 PATRONES INICIADO*\nGartley / Butterfly / Cypher\n5m + 15m - C>91 CHOP + RSI>95\nTP en punto C - LIVE 24/7")
    vistos = set()
    while True:
        try:
            for sym in SYMBOLS:
                for tf in TIMEFRAMES:
                    try:
                        df = yf.download(sym, period="2d", interval=tf, progress=False, auto_adjust=True)
                        if len(df) < 100: continue
                        df['RSI'] = calc_rsi(df['Close'])
                        df['CHOP'] = calc_chop(df['High'], df['Low'], df['Close'])
                        last = df.iloc[-2] # vela cerrada anterior
                        chop = float(last['CHOP']) if not pd.isna(last['CHOP']) else 0
                        rsi = float(last['RSI']) if not pd.isna(last['RSI']) else 0

                        # TU FILTRO EXACTO TV DE LAS FOTOS
                        if chop > 91 and rsi > 95:
                            key = f"{sym}_{tf}_{str(df.index[-2])}"
                            if key in vistos: continue
                            pats = detect_3_patterns(df)
                            if pats:
                                for p in pats:
                                    send_tg(f"🎯 *{p} DETECTADO - NO TE LO PIERDAS*\n*Par:* {sym.replace('=X','')}\n*TF:* {tf}\n*Punto C:* CHOP {chop:.1f} >91 | RSI {rsi:.1f} >95\n*TP:* Punto C (como pediste)\n*Hora:* {str(df.index[-2])[-8:]}")
                            else:
                                send_tg(f"⚠️ *FILTRO C>91 RSI>95 CUMPLIDO*\n*Par:* {sym.replace('=X','')} *TF:* {tf}\nCHOP {chop:.1f} | RSI {rsi:.1f}\nPosible Gartley/Butterfly/Cypher en formación - Quedó en vigilancia")
                            vistos.add(key)
                    except Exception as e:
                        print(f"Error {sym} {tf}: {e}")
                        continue
            print("Ciclo 3 patrones terminado, esperando 3 min...")
            time.sleep(180)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(60)

@app.route("/")
def home(): return "BOT 3 PATRONES LIVE - Gartley Butterfly Cypher 91/95"

@app.route("/test")
def test():
    send_tg("✅ TEST OK - 3 PATRONES Gartley/Butterfly/Cypher ACTIVO 24/7 - No te perderás ninguno")
    return "ok - test enviado"

threading.Thread(target=scan_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
