def decompose(prompt):
    return {
        "branches": [
            {"id": "direct", "weight": 0.7},
            {"id": "structured", "weight": 1.0},
            {"id": "exploratory", "weight": 0.6}
        ]
    }
