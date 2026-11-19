def next_commands(event, order):
    if order["qty"] <= 10:
        if order["price"] * order["qty"] <= event["cash"] - event["reserved"]:
            return [{"type": "approve"}]
    return []