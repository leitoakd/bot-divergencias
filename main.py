from flask import Flask, request
import os
import requests
app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(e)
@app.route("/")
def home():
    return "Bot LEO EURUSD - Online", 200
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.data.decode("utf-8") if request.data else ""
    if not msg:
        msg = str(request.get_json(silent=True))
    print(f"Recibido: {msg}")
    ml = msg.lower()
    if "gartley" in ml or "butterfly" in ml or "cypher" in ml:
        send_telegram(f"🔔 ARMONICO EURUSD\n\n{msg}")
        return "enviado", 200
    else:
        return "ignorado", 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
