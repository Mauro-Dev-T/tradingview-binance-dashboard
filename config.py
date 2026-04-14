import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 Binance
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

# 🔐 Webhook
SECRET = os.getenv("SECRET", "mysecret")

# ⚙️ Trading
TRADE_USDT_AMOUNT = float(os.getenv("TRADE_USDT_AMOUNT", "10"))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", "0.005"))
ENABLE_AUTO_EXECUTE = os.getenv("ENABLE_AUTO_EXECUTE", "true").lower() == "true"

# 🗄️ Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "trading.db")

# 🌐 Dashboard
DASHBOARD_USER = os.getenv("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS", "admin123")
