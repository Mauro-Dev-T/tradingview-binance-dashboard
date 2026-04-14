import requests
import time

URL = "http://localhost:5002/webhook"

signals = [
    {"symbol": "BTCUSDT", "price": "65000", "side": "BUY"},
    {"symbol": "ETHUSDT", "price": "3200",  "side": "SELL"},
    {"symbol": "SOLUSDT", "price": "150",   "side": "BUY"},
]

print("🚀 Demo Módulo 3 — Full System + Dashboard\n")

for signal in signals:
    data = {
        "secret": "mysecret",
        "symbol": signal["symbol"],
        "price": signal["price"],
        "side": signal["side"],
        "quantity_usdt": 10,
    }

    try:
        response = requests.post(URL, json=data, timeout=10)
        result = response.json()
        print(f"✅ {signal['symbol']} {signal['side']} → {response.status_code} | {result.get('status')}")
    except Exception as e:
        print(f"❌ {signal['symbol']} → Error: {e}")

    time.sleep(3)

print("\n✅ Demo finalizado — Abrí http://localhost:5002 para ver el dashboard")
