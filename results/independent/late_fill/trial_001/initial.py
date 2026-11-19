def next_commands(event, order):
    if not event["seen"] and event["qty"] > 0 and order["filled"] < order["qty"]:
        if order["status"] == "cancelled":
            if event["qty"] + order["filled"] <= order["qty"]:
                return [{"type": "apply_fill", "qty": event["qty"]}]
            else:
                return [{"type": "apply_fill", "qty": order["qty"] - order["filled"]}]
        elif order["status"] != "cancelled":
            return [{"type": "apply_fill", "qty": event["qty"]}]
    return []