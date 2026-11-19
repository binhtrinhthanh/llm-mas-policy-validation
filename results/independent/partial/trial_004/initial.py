def next_commands(event, order):
    if event["kind"] == "fill" and not event["seen"]:
        already_filled = order.get("filled", 0)
        total_qty = order.get("qty", 0)
        fill_qty = event.get("qty", 0)
        applied_qty = min(fill_qty, total_qty - already_filled)
        if applied_qty > 0:
            return [{"type": "apply_fill", "qty": applied_qty}]
    return []