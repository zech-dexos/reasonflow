"""
sigil_memory_bridge.py — ReasonFlow / DexOS Integration
Writes sigil lifecycle events to dex_memory.jsonl so Dex
builds reasoned memory, not just logged memory.

Drop in: ~/reasonflow/reasonflow/sigil_memory_bridge.py
"""

import json
import os
import time
from pathlib import Path

# Matches DexOS memory path
MEMORY_FILE = os.path.expanduser("~/dexos/subconscious/dex_memory.jsonl")
FALLBACK_FILE = os.path.expanduser("~/.reasonflow/dex_memory.jsonl")


def _get_memory_path() -> str:
    p = Path(MEMORY_FILE)
    if p.parent.exists():
        return MEMORY_FILE
    # fallback: write next to sigils.json
    Path(FALLBACK_FILE).parent.mkdir(parents=True, exist_ok=True)
    return FALLBACK_FILE


def _write(entry: dict):
    path = _get_memory_path()
    entry["ts"] = round(time.time(), 3)
    entry["source"] = "reasonflow:sigil"
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ─────────────────────────────────────────────
# PUBLIC HOOKS — call these from SigilMemory
# ─────────────────────────────────────────────

def record_activation(sigil, context: str, score: float):
    """Called when a sigil activates during a reasoning cycle."""
    _write({
        "event": "sigil_activation",
        "sigil_id": sigil.id,
        "sigil": str(sigil),
        "context": context,
        "score": round(score, 4),
        "strength": round(sigil.strength, 4),
        "activation_count": sigil.activation_count,
    })


def record_reinforcement(sigil, delta: float):
    """Called when a sigil is reinforced after good outcome."""
    _write({
        "event": "sigil_reinforcement",
        "sigil_id": sigil.id,
        "sigil": str(sigil),
        "delta": round(delta, 4),
        "new_strength": round(sigil.strength, 4),
        "new_confidence": round(sigil.confidence, 4),
    })


def record_decay(sigil, old_strength: float):
    """Called when a sigil decays from disuse."""
    delta = old_strength - sigil.strength
    if delta < 0.001:
        return  # not worth logging tiny decay
    _write({
        "event": "sigil_decay",
        "sigil_id": sigil.id,
        "sigil": str(sigil),
        "old_strength": round(old_strength, 4),
        "new_strength": round(sigil.strength, 4),
        "delta": round(delta, 4),
    })


def record_creation(sigil, trigger: str = "explicit"):
    """Called when a new sigil is created."""
    _write({
        "event": "sigil_creation",
        "sigil_id": sigil.id,
        "sigil": str(sigil),
        "trigger": trigger,
        "initial_strength": round(sigil.strength, 4),
    })


def record_mutation(old_sigil, new_name: str, reason: str = "correction"):
    """Called when a sigil mutates."""
    _write({
        "event": "sigil_mutation",
        "sigil_id": old_sigil.id,
        "old_name": old_sigil.name,
        "new_name": new_name,
        "reason": reason,
        "strength_after": round(old_sigil.strength, 4),
    })


def record_conflict_resolution(winner, losers: list, context: str):
    """Called when competing sigils are resolved."""
    _write({
        "event": "sigil_conflict_resolved",
        "winner": str(winner),
        "losers": [str(s) for s in losers],
        "context": context,
        "winner_strength": round(winner.strength, 4),
    })


def record_cycle(trace: dict):
    """Called at end of each ReasonFlow cycle with full trace."""
    _write({
        "event": "reasonflow_cycle",
        "trace_id": trace.get("trace_id"),
        "context": trace.get("context"),
        "selected_branch": trace.get("selected", {}).get("id"),
        "active_sigils": trace.get("active_sigils", []),
        "specialized_model": trace.get("specialized_model"),
    })


def read_recent(n: int = 20) -> list:
    """Read last N sigil events from memory. Used by dex_digest."""
    path = _get_memory_path()
    if not os.path.exists(path):
        return []
    lines = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("source") == "reasonflow:sigil":
                        lines.append(entry)
                except:
                    pass
    return lines[-n:]


def summarize_sigil_history() -> dict:
    """
    Returns a summary Dex can use in longmind / digest.
    Called by dex_digest.py to feed sigil context into Dex.
    """
    events = read_recent(100)
    if not events:
        return {"summary": "No sigil history yet.", "events": 0}

    activations = [e for e in events if e["event"] == "sigil_activation"]
    reinforcements = [e for e in events if e["event"] == "sigil_reinforcement"]
    mutations = [e for e in events if e["event"] == "sigil_mutation"]
    decays = [e for e in events if e["event"] == "sigil_decay"]

    # most activated sigils
    counts = {}
    for e in activations:
        sid = e.get("sigil", "unknown")
        counts[sid] = counts.get(sid, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "summary": f"{len(events)} sigil events in memory.",
        "events": len(events),
        "activations": len(activations),
        "reinforcements": len(reinforcements),
        "mutations": len(mutations),
        "decays": len(decays),
        "top_active_sigils": [{"sigil": s, "count": c} for s, c in top],
        "recent_mutations": [
            {"from": e["old_name"], "to": e["new_name"]} for e in mutations[-3:]
        ],
    }
