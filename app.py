from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from datetime import datetime
from functools import wraps

from config import SECRET, ENABLE_AUTO_EXECUTE, DASHBOARD_USER, DASHBOARD_PASS
from signal_parser import parse_signal
from binance_executor import execute_market_order, get_account_balance, get_open_orders
from database import init_db, save_signal, save_order, get_signals, get_orders, get_stats

app = Flask(__name__)
app.secret_key = "tradingbot_secret_key_module3"

# Inicializar DB al arrancar
init_db()


# ─────────────────────────────────────────
# 🔐 AUTH
# ─────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] == DASHBOARD_USER and request.form["password"] == DASHBOARD_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─────────────────────────────────────────
# 🌐 DASHBOARD
# ─────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    stats = get_stats()
    signals = get_signals(limit=10)
    orders = get_orders(limit=10)
    balance = get_account_balance()
    open_orders = get_open_orders()

    return render_template("dashboard.html",
        stats=stats,
        signals=signals,
        orders=orders,
        balance=balance,
        open_orders=open_orders,
        auto_execute=ENABLE_AUTO_EXECUTE,
    )


# ─────────────────────────────────────────
# 📡 API ENDPOINTS (para el dashboard)
# ─────────────────────────────────────────

@app.route("/api/balance")
@login_required
def api_balance():
    return jsonify(get_account_balance())


@app.route("/api/open-orders")
@login_required
def api_open_orders():
    return jsonify(get_open_orders())


@app.route("/api/signals")
@login_required
def api_signals():
    return jsonify(get_signals(limit=50))


@app.route("/api/orders")
@login_required
def api_orders():
    return jsonify(get_orders(limit=50))


@app.route("/api/stats")
@login_required
def api_stats():
    return jsonify(get_stats())


# ─────────────────────────────────────────
# 🌐 WEBHOOK
# ─────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"[{datetime.now()}] Incoming: {data}")

    if not data or data.get("secret") != SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    signal = parse_signal(data)
    if not signal:
        return jsonify({"error": "Invalid signal data"}), 400

    # Guardar señal en DB
    signal_id = save_signal(signal)
    print(f"[{datetime.now()}] Signal saved: ID {signal_id}")

    # Ejecutar orden si está habilitado y hay side
    if ENABLE_AUTO_EXECUTE and signal.get("side"):
        print(f"[{datetime.now()}] Executing: {signal['side']} {signal['symbol']}")
        order = execute_market_order(signal)
        save_order(signal_id, order)

        if order["success"]:
            print(f"[{datetime.now()}] Order executed: {order['order_id']}")
            return jsonify({"status": "signal saved + order executed", "order_id": order["order_id"]}), 200
        else:
            print(f"[{datetime.now()}] Order failed: {order['error']}")
            return jsonify({"status": "signal saved, order failed", "error": order["error"]}), 200

    return jsonify({"status": "signal saved (no execution)"}), 200


# ─────────────────────────────────────────
# 🏥 HEALTH
# ─────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "module": "3 - Full System + Dashboard",
        "auto_execute": ENABLE_AUTO_EXECUTE,
        "timestamp": datetime.now().isoformat(),
    }), 200


# ─────────────────────────────────────────
# ▶️ RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
