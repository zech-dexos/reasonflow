from .talnir import decompose
from .dex import select
from .memory import load_state, save_state
from .llm import run_llm
from .sigil import SigilMemory
import uuid

_sigil_memory = SigilMemory()

def run(prompt, config=None):
    config = config or {}
    state = load_state()
    trace_id = str(uuid.uuid4())

    context = "CTX:ALL"
    p = prompt.lower()
    if any(w in p for w in ["code", "function", "debug", "script"]):
        context = "CTX:CODING"
    elif any(w in p for w in ["plan", "design", "architect"]):
        context = "CTX:PLANNING"
    elif any(w in p for w in ["run", "execute", "tool", "command"]):
        context = "CTX:TOOL"

    active_sigils = _sigil_memory.activate_for_context(context)
    resolved = _sigil_memory.resolve_conflicts(active_sigils, context)
    graph = decompose(prompt)
    graph["branches"] = _sigil_memory.apply_to_branches(graph["branches"], resolved)
    chosen = select(graph)
    output = run_llm(prompt, chosen, config)

    trace = {
        "trace_id": trace_id,
        "input": prompt,
        "context": context,
        "active_sigils": [str(s) for s in resolved],
        "branches": graph["branches"],
        "selected": chosen,
        "output": output
    }

    state["last"] = trace
    save_state(state)
    return trace
