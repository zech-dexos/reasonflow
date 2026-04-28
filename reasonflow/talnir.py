def decompose(prompt):
    p = prompt.lower()
    branches = [
        {"id": "direct", "weight": 0.7},
        {"id": "structured", "weight": 0.6},
        {"id": "exploratory", "weight": 0.5},
    ]
    if any(w in p for w in ["debug", "error", "fix", "broken", "crash"]):
        branches.append({"id": "debug_first", "weight": 0.85})
    if any(w in p for w in ["plan", "design", "architect", "build"]):
        branches.append({"id": "planning", "weight": 0.85})
    if any(w in p for w in ["run", "execute", "command", "tool"]):
        branches.append({"id": "tool_execution", "weight": 0.85})
    return {"branches": branches}
