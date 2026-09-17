import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import yfinance as yf
import requests

# --- Servidor falso para que Render no falle (NO BORRAR) ---
def start_fake_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot running")
        def log_message(self, *args): return
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

# --- Bot ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print("Bot iniciado...")

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

while True:
    try:
        df = yf.download("GBPUSD=X", period="1d", interval="15m")
        precio = df['Close'].iloc[-1]
        print(f"GBPUSD: {precio}")
        # acá después le agregamos la lógica de divergencias
    except Exception as e:
        print(e)
    time.sleep(60)
