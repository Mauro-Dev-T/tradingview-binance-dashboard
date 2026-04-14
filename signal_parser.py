import re


def parse_signal(data: dict) -> dict:
    symbol = _parse_symbol(data.get("symbol", ""))
    price = _parse_price(data.get("price", 0))
    side = _parse_side(data.get("side", ""))
    quantity_usdt = float(data.get("quantity_usdt", 0))

    if not symbol or price <= 0:
        return {}

    risk = float(data.get("risk_percent", 0.005))
    sl, tp = _calculate_sl_tp(price, side, risk)

    return {
        "symbol": symbol,
        "price": price,
        "side": side,
        "sl": sl,
        "tp": tp,
        "risk": risk,
        "quantity_usdt": quantity_usdt,
    }


def _parse_symbol(raw: str) -> str:
    return raw.upper().replace("/", "").replace("-", "").strip()


def _parse_price(raw) -> float:
    try:
        return float(str(raw).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def _parse_side(raw: str) -> str:
    raw = raw.upper().strip()
    if raw in ("BUY", "LONG", "COMPRA"):
        return "BUY"
    if raw in ("SELL", "SHORT", "VENTA"):
        return "SELL"
    return ""


def _calculate_sl_tp(price: float, side: str, risk: float) -> tuple:
    if side == "BUY":
        sl = round(price * (1 - risk), 5)
        tp = round(price * (1 + risk * 2), 5)
    elif side == "SELL":
        sl = round(price * (1 + risk), 5)
        tp = round(price * (1 - risk * 2), 5)
    else:
        sl = round(price * (1 - risk), 5)
        tp = round(price * (1 + risk * 2), 5)
    return sl, tp
