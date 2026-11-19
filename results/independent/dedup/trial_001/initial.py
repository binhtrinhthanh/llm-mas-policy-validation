def next_commands(event, order):
    if event.get("seen"):
        return []
    if event.get("qty") + order.get("filled", 0) > order.get("qty", 0):
        return []
    return [{"type": "apply_fill", "qty": event["qty"]}]