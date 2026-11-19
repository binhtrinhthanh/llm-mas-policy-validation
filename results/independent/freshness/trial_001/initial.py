def next_commands(event, order):
    if event.get("kind") == "quote":
        age = event.get("age")
        if age is not None and age > 5:
            return []
        else:
            return [{"type": "forward"}]
    else:
        return [{"type": "forward"}]