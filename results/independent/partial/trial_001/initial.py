def next_commands(event, order):
    if event["kind"] == "fill" and not event["seen"]:
        q = event["qty"]
        filled = order["filled"]
        total_qty = order["qty"]
        if order["status"] == "cancelled" or filled >= total_qty:
            return [{"type": "apply_fill", "qty": q}]
        elif filled + q <= total_qty:
            return [{"type": "apply_fill", "qty": q}]
        else:
            return [{"type": "apply_fill", "qty": total_qty - filled}]
    return []