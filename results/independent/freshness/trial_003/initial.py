def next_commands(event, order):
    if event.get("kind") == "quote":
        if event.get("age", 0) <= 5:
            return [{"type": "forward"}]
        else:
            return []
    else:
        return [{"type": "forward"}]