def select(graph):
    return max(graph["branches"], key=lambda b: b["weight"])
