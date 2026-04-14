from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_TESTNET, TRADE_USDT_AMOUNT
import math


def _get_client() -> Client:
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    if BINANCE_TESTNET:
        client.API_URL = "https://testnet.binance.vision/api"
    return client


def get_account_balance() -> list:
    """Retorna balances con valor > 0."""
    try:
        client = _get_client()
        account = client.get_account()
        balances = [
            b for b in account["balances"]
            if float(b["free"]) > 0 or float(b["locked"]) > 0
        ]
        return balances
    except Exception as e:
        return []


def get_open_orders() -> list:
    """Retorna todas las órdenes abiertas."""
    try:
        client = _get_client()
        orders = client.get_open_orders()
        return orders
    except Exception as e:
        return []


def _round_quantity(quantity: float, step_size: str) -> float:
    step = float(step_size)
    precision = int(round(-math.log(step, 10), 0))
    return round(math.floor(quantity / step) * step, precision)


def calculate_quantity(symbol: str, price: float, usdt_amount: float) -> float:
    amount = usdt_amount if usdt_amount > 0 else TRADE_USDT_AMOUNT
    raw_qty = amount / price
    try:
        client = _get_client()
        info = client.get_symbol_info(symbol)
        step_size = "1"
        for f in info["filters"]:
            if f["filterType"] == "LOT_SIZE":
                step_size = f["stepSize"]
                break
        return _round_quantity(raw_qty, step_size)
    except Exception:
        return round(raw_qty, 6)


def execute_market_order(signal: dict) -> dict:
    symbol = signal.get("symbol")
    side = signal.get("side")
    price = signal.get("price")
    usdt_amount = signal.get("quantity_usdt", 0)

    if not symbol or not side or not price:
        return {"success": False, "error": "Datos de señal incompletos"}

    if side not in ("BUY", "SELL"):
        return {"success": False, "error": f"Side inválido: {side}"}

    try:
        client = _get_client()
        quantity = calculate_quantity(symbol, price, usdt_amount)

        if quantity <= 0:
            return {"success": False, "error": "Cantidad calculada inválida"}

        order = client.create_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )

        return {
            "success": True,
            "order_id": order.get("orderId"),
            "symbol": order.get("symbol"),
            "side": order.get("side"),
            "quantity": order.get("executedQty"),
            "status": order.get("status"),
            "fills": order.get("fills", []),
        }

    except BinanceAPIException as e:
        return {"success": False, "error": f"Binance API error: {e.message}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
