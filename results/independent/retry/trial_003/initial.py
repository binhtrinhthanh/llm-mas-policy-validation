def next_commands(event, order):
    if order["approved"] and order["status"] == "approved":
        if event["kind"] == "submit":
            return [{"type": "submit", "client_order_id": order["order_id"], "price": order["price"], "qty": order["qty"]}]
        elif event["kind"] == "timeout":
            return [{"type": "submit", "client_order_id": order["order_id"], "price": order["price"], "qty": order["qty"]}]
    return []