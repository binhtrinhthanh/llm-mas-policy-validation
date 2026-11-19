def next_commands(event, order):
    if not event["seen"]:
        if order["status"] != "cancelled":
            return [{"type": "apply_fill", "qty": event["qty"]}]
        elif order["filled"] < order["qty"]:
            return [{"type": "apply_fill", "qty": event["qty"]}]
    return []