def next_commands(event, order):
    if event.get("kind") != "fill":
        return []
    if event.get("seen", False):
        return []
    filled = order.get("filled", 0)
    total = order.get("qty", 0)
    if filled >= total and order.get("status") == "cancelled":
        return []
    return [{"type": "apply_fill", "qty": event["qty"]}]