from __future__ import annotations
from typing import Dict, Tuple, List
from .utils import SHIPPING_FLAT

def apply_promos(codes: set[str], subtotal: float, lines: list[dict], shipping: float) -> tuple[float, float, list[str]]:
    discount = 0.0
    ship_disc = 0.0
    messages: list[str] = []
    codes = {c.strip().upper() for c in codes if c.strip()}

    if "WELCOME10" in codes:
        d = round(subtotal * 0.10, 2)
        discount += d
        messages.append(f"WELCOME10 applied: -R{d:.2f}")

    if "BULK5" in codes:
        bulk_base = sum(l['unit_price'] * l['qty'] for l in lines if l['qty'] >= 5)
        if bulk_base > 0:
            d = round(bulk_base * 0.05, 2)
            discount += d
            messages.append(f"BULK5 applied: -R{d:.2f}")

    if "FREESHIP" in codes and shipping > 0:
        sd = min(SHIPPING_FLAT, shipping)
        ship_disc += sd
        if sd > 0:
            messages.append(f"FREESHIP applied: -R{sd:.2f} shipping")

    return round(discount, 2), round(ship_disc, 2), messages
