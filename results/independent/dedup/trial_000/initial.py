def next_commands(event, order):
    if event.get("seen"):
        return []
    if event.get("kind") == "fill":
        new_fill = event.get("qty", 0)
        if new_fill <= 0:
            return []
        filled_before = order.get("filled", 0)
        total_qty = order.get("qty", 0)
        # allow applies if new_fill + filled_before <= total_qty or order is canceled (status other than active)
        status = order.get("status", "")
        if filled_before + new_fill <= total_qty or status != "active":
            return [{"type": "apply_fill", "qty": new_fill}]
    return []