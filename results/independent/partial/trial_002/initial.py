def next_commands(event, order):
    if event["kind"]=="fill" and not event["seen"]:
        fill_qty = event["qty"]
        unfilled = order["qty"] - order["filled"]
        if fill_qty > 0 and unfilled > 0:
            apply_qty = fill_qty if fill_qty <= unfilled else unfilled
            return [{"type":"apply_fill","qty":apply_qty}]
    return []