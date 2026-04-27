from .talnir import decompose
from .dex import select
from .memory import load_state, save_state
from .llm import run_llm
import uuid


def run(prompt, config=None):
    config = config or {}

    state = load_state()

    trace_id = str(uuid.uuid4())

    graph = decompose(prompt)
    chosen = select(graph)
    output = run_llm(prompt, chosen, config)

    trace = {
        "trace_id": trace_id,
        "input": prompt,
        "branches": graph["branches"],
        "selected": chosen,
        "output": output
    }

    state["last"] = trace
    save_state(state)

    return trace
