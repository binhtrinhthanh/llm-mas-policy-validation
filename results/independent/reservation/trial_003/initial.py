def next_commands(event, order):
    cost = order["price"] * order["qty"]
    max_qty = 10
    if order["qty"] > max_qty:
        return []
    if cost <= event["cash"] - event["reserved"]:
        return [{"type": "approve"}]
    return []