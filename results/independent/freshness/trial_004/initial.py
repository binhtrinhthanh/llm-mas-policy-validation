def next_commands(event, order):
    if event.get("kind") == "quote" and event.get("age", 0) > 5:
        return []
    else:
        return [{"type": "forward"}]