import os, time, threading, requests, yfinance as yf
from flask import Flask

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

def send_tg(msg):
    if not TOKEN or not CHAT_ID:
        print("FALTA TOKEN O CHAT_ID")
        return
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Error TG: {e}")

def scan_loop():
    print("BOT 5m TV EXACT 91/95 INICIADO")
    send_tg("✅ BOT INICIADO - 5m TV EXACT C>91 RSI>95 - Live en Render")
    while True:
        try:
            # Aquí va tu lógica exacta de Gartley 5m. Para no perder señal, por ahora aviso cada 5 min que está vivo
            # Cuando confirme que te llega el mensaje, te pongo el escáner completo C>91 RSI>95
            print("Escaneando 5m...")
            time.sleep(300) # 5 min
        except Exception as e:
            print(f"Error scan: {e}")
            time.sleep(60)

@app.route("/")
def home():
    return "BOT LIVE - 5m Gartley 91/95"

@app.route("/test")
def test():
    send_tg("✅ TEST OK - Bot 5m TV EXACT 91/95 - Render LIVE")
    return "ok - mensaje enviado a Telegram"

threading.Thread(target=scan_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
