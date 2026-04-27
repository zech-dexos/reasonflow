def run_llm(prompt, choice, config=None):
    config = config or {}

    if choice["id"] == "structured":
        return "[ReasonFlow Structured] " + prompt

    return "[ReasonFlow Direct] " + prompt
