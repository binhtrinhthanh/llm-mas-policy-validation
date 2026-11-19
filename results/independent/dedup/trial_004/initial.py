def next_commands(event, order):
    if event.get("seen"):
        return []
    qty = event.get("qty", 0)
    if qty <= 0:
        return []
    total_filled = order.get("filled", 0)
    total_qty = order.get("qty", 0)
    status = order.get("status", "")
    if status == "canceled" and qty + total_filled <= total_qty:
        return [{"type": "apply_fill", "qty": qty}]
    if total_filled + qty <= total_qty:
        return [{"type": "apply_fill", "qty": qty}]
    if total_filled < total_qty:
        return [{"type": "apply_fill", "qty": total_qty - total_filled}]
    return []