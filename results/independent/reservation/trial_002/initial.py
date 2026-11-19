def next_commands(event, order):
    cost = order["price"] * order["qty"]
    available = event["cash"] - event["reserved"]
    if cost <= available and order["qty"] <= 10:
        return [{"type": "approve"}]
    return []