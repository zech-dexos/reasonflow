def select(graph, prompt):
    best = None
    best_score = -1

    for b in graph["branches"]:
        score = b["weight"]

        if "plan" in prompt.lower() and b["id"] == "structured":
            score += 0.3

        if len(prompt) < 20 and b["id"] == "direct":
            score += 0.2

        if score > best_score:
            best = b
            best_score = score

    return best
