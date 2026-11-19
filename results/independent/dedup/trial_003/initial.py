def next_commands(event, order):
    if event.get("kind") != "fill":
        return []
    if event.get("seen", False):
        return []
    qty = event.get("qty", 0)
    filled = order.get("filled", 0)
    total = order.get("qty", 0)
    if filled >= total:
        # Already fully filled, but if a new fill notification arrives (late), still apply it
        return [{"type": "apply_fill", "qty": qty}]
    else:
        # Not fully filled yet, apply fill normally
        return [{"type": "apply_fill", "qty": qty}]