from .talnir import decompose
from .dex import select
from .memory import load_state, save_state
from .sigil import SigilMemory
import uuid
import subprocess
import json

_sigil_memory = SigilMemory()

# Branch to model mapping
# Each branch routes to a specialized brain
BRANCH_MODELS = {
    "debug_first":    "qwen2.5-coder:0.5b",
    "structured":     None,  # use passed-in LLM or default
    "direct":         None,
    "exploratory":    None,
    "planning":       None,
    "tool_execution": "qwen2.5-coder:0.5b",
}

def run_model(prompt, model, config=None):
    """Run a specific ollama model and return response."""
    if model is None:
        # No specialized brain — return structured marker
        return f"[ReasonFlow:{model or 'default'}] {prompt}"
    
    try:
        result = subprocess.run(
            ["ollama", "run", model, 
             f"Extract the key technical structure from this in 3 lines maximum. Be concise. No explanation: {prompt}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"[timeout: {model}]"
    except Exception as e:
        return f"[error: {e}]"

def run(prompt, config=None):
    config = config or {}
    state = load_state()
    trace_id = str(uuid.uuid4())

    # Detect context
    context = "CTX:ALL"
    p = prompt.lower()
    if any(w in p for w in ["code", "function", "debug", "script", "bash", "python"]):
        context = "CTX:CODING"
    elif any(w in p for w in ["plan", "design", "architect", "build"]):
        context = "CTX:PLANNING"
    elif any(w in p for w in ["run", "execute", "command", "tool"]):
        context = "CTX:TOOL"

    # Activate sigils
    active_sigils = _sigil_memory.activate_for_context(context)
    resolved = _sigil_memory.resolve_conflicts(active_sigils, context)

    # Build reasoning graph
    graph = decompose(prompt)

    # Apply sigil biases
    graph["branches"] = _sigil_memory.apply_to_branches(
        graph["branches"], resolved
    )

    # Select winning branch
    chosen = select(graph)

    # Route to specialized brain if available
    specialized_model = BRANCH_MODELS.get(chosen["id"])
    preprocessed = None

    if specialized_model:
        preprocessed = run_model(prompt, specialized_model, config)
        output = f"[preprocessed by {specialized_model}]\n{preprocessed}"
    else:
        output = f"[ReasonFlow:{chosen['id']}] {prompt}"

    trace = {
        "trace_id": trace_id,
        "input": prompt,
        "context": context,
        "active_sigils": [str(s) for s in resolved],
        "branches": graph["branches"],
        "selected": chosen,
        "specialized_model": specialized_model,
        "preprocessed": preprocessed,
        "output": output
    }

    state["last"] = trace
    save_state(state)
    return trace
