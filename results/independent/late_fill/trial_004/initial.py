def next_commands(event, order):
    if event["seen"]:
        return []
    if event["qty"] == 0:
        return []
    if order["status"] == "cancelled":
        remaining = order["qty"] - order["filled"]
        if remaining > 0 and event["qty"] <= remaining:
            return [{"type": "apply_fill", "qty": event["qty"]}]
        else:
            return []
    if order["status"] != "cancelled":
        return [{"type": "apply_fill", "qty": event["qty"]}]
    return []