def next_commands(event, order):
    age = event.get("age", 0)
    if event.get("kind") == "quote" and age > 5:
        return []
    else:
        return [{"type": "forward"}]