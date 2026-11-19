def next_commands(event, order):
    if event["kind"] == "fill" and not event["seen"]:
        fill_qty = event["qty"]
        already_filled = order.get("filled", 0)
        total_order_qty = order.get("qty", 0)
        if already_filled + fill_qty <= total_order_qty:
            return [{"type": "apply_fill", "qty": fill_qty}]
        elif already_filled < total_order_qty:
            return [{"type": "apply_fill", "qty": total_order_qty - already_filled}]
        else:
            return []
    return []