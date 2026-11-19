def next_commands(event, order):
    if not event["seen"]:
        apply_qty = event["qty"]
        if order["status"] == "canceled" and (order["filled"] + apply_qty) > order["qty"]:
            return []
        if apply_qty + order["filled"] > order["qty"]:
            apply_qty = order["qty"] - order["filled"]
        if apply_qty > 0:
            return [{"type": "apply_fill", "qty": apply_qty}]
    return []