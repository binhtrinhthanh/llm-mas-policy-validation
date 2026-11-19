def next_commands(event, order):
    total_cost = order["price"] * order["qty"]
    available_cash = event["cash"] - event["reserved"]
    if total_cost <= available_cash and order["qty"] <= 10:
        return [{"type": "approve"}]
    return []