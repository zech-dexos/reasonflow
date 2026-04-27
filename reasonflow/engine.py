from reasonflow.talnir import decompose
from reasonflow.dex import select
from reasonflow.llm import run_llm
from reasonflow.memory import load_state, save_state

def run(prompt):
    state = load_state()

    graph = decompose(prompt)
    choice = select(graph, prompt)
    output = run_llm(prompt, choice)

    trace = {
        "input": prompt,
        "branches": graph["branches"],
        "selected": choice,
        "output": output
    }

    state["last"] = trace
    save_state(state)

    return trace
