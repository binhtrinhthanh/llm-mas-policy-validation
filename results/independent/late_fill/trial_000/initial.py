def next_commands(event, order):
    if not event["seen"] and event["qty"] > 0:
        if order["status"] != "cancelled":
            return [{"type": "apply_fill", "qty": event["qty"]}]
        elif order["status"] == "cancelled" and order["filled"] < order["qty"]:
            return [{"type": "apply_fill", "qty": event["qty"]}]
    return []