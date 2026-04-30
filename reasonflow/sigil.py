"""
Sigil System v2 — ReasonFlow Memory Layer
Author: Zech (Root) / Deximus Maximus

Upgrades from v1:
- Memory bridge: all lifecycle events write to dex_memory.jsonl
- Decay floor: sigils never fully die (ghost bias prevention)
- Reinforcement: diminishing returns curve
- Mutation: preserves semantic lineage
- Conflict resolution: logs winner to memory
- All existing API preserved — drop-in replacement
"""

import json, os, time, uuid
from dataclasses import dataclass, field, asdict

# Import bridge — graceful fallback if not present
try:
    from .sigil_memory_bridge import (
        record_activation, record_reinforcement,
        record_decay, record_creation, record_mutation,
        record_conflict_resolution
    )
    BRIDGE_ACTIVE = True
except ImportError:
    try:
        from sigil_memory_bridge import (
            record_activation, record_reinforcement,
            record_decay, record_creation, record_mutation,
            record_conflict_resolution
        )
        BRIDGE_ACTIVE = True
    except ImportError:
        BRIDGE_ACTIVE = False
        def record_activation(*a, **k): pass
        def record_reinforcement(*a, **k): pass
        def record_decay(*a, **k): pass
        def record_creation(*a, **k): pass
        def record_mutation(*a, **k): pass
        def record_conflict_resolution(*a, **k): pass

SIGIL_FILE = os.path.expanduser("~/.reasonflow/sigils.json")

# Governance constants
DOMINANCE_CAP    = 0.92
DECAY_FLOOR      = 0.10   # sigils never fully vanish
DECAY_WINDOW_SEC = 3600   # 1 hour before decay kicks in
MAX_ACTIVE_SET   = 5


@dataclass
class Sigil:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = "PREF"
    name: str = ""
    mode: str = "DRIFT"
    context: str = "CTX:ALL"
    strength: float = 0.6
    confidence: float = 0.5
    created_at: float = field(default_factory=time.time)
    last_activated: float = 0.0
    activation_count: int = 0
    decay_rate: float = 0.02
    failure_count: int = 0        # NEW: tracks corrections for mutation

    def __post_init__(self):
        if self.last_activated == 0.0:
            self.last_activated = self.created_at

    def activate(self):
        self.strength = min(DOMINANCE_CAP, self.strength + 0.05)
        self.last_activated = time.time()
        self.activation_count += 1

    def reinforce(self):
        # v2: diminishing returns — delta shrinks as strength grows
        delta = 0.1 * (1.0 - self.strength)
        old_strength = self.strength
        self.strength = min(DOMINANCE_CAP, self.strength + delta)
        self.confidence = min(1.0, self.confidence + 0.05)
        record_reinforcement(self, self.strength - old_strength)

    def decay(self):
        if self.mode == "LOCK":
            return
        age = time.time() - self.last_activated
        if age > DECAY_WINDOW_SEC:
            old = self.strength
            # v2: exponential decay with floor — never fully vanishes
            self.strength = max(
                DECAY_FLOOR,
                self.strength * (1.0 - self.decay_rate)
            )
            record_decay(self, old)

    def mutate(self, new_name, reason: str = "correction"):
        # v2: preserve lineage — log what it was before changing
        record_mutation(self, new_name, reason)
        self.name = new_name
        self.mode = "DRIFT"
        self.strength = max(0.3, self.strength - 0.1)
        self.failure_count = 0  # reset after mutation

    def score(self, context):
        if self.context != "CTX:ALL" and self.context != context:
            return 0.0
        recency = 1.0 / (1.0 + (time.time() - self.last_activated) / 3600)
        return self.strength * self.confidence * recency

    def __str__(self):
        return f"[{self.type}:{self.name}:{self.mode}:{self.context}] s={self.strength:.2f}"


class SigilMemory:
    def __init__(self):
        os.makedirs(os.path.dirname(SIGIL_FILE), exist_ok=True)
        self.sigils = []
        self.load()

    def load(self):
        if os.path.exists(SIGIL_FILE):
            try:
                data = json.load(open(SIGIL_FILE))
                self.sigils = [Sigil(**s) for s in data]
            except:
                self.sigils = []

    def save(self):
        json.dump([asdict(s) for s in self.sigils],
                  open(SIGIL_FILE, "w"), indent=2)

    def create(self, type, name, mode="DRIFT",
               context="CTX:ALL", strength=0.6, trigger="explicit"):
        s = Sigil(type=type, name=name, mode=mode,
                  context=context, strength=strength)
        self.sigils.append(s)
        self.save()
        # v2: write creation to dex_memory.jsonl
        record_creation(s, trigger=trigger)
        return s

    def activate_for_context(self, context):
        active = []
        for s in self.sigils:
            s.decay()
            score = s.score(context)
            if score > 0.1:
                s.activate()
                # v2: write activation to dex_memory.jsonl
                record_activation(s, context, score)
                active.append(s)
        active.sort(key=lambda s: s.score(context), reverse=True)
        self.save()
        return active

    def resolve_conflicts(self, active, context):
        resolved = sorted(active,
                          key=lambda s: s.score(context),
                          reverse=True)[:MAX_ACTIVE_SET]
        # v2: log conflict resolution if there were actual competing sigils
        if len(active) > 1 and resolved:
            losers = [s for s in active if s not in resolved]
            record_conflict_resolution(resolved[0], losers, context)
        return resolved

    def apply_to_branches(self, branches, active_sigils):
        modified = []
        for b in branches:
            weight = b["weight"]
            for s in active_sigils:
                if s.type == "HEUR" and s.name.lower() in b["id"].lower():
                    weight = min(1.0, weight + s.strength * 0.2)
                if s.type == "RISK" and s.name.lower() in b["id"].lower():
                    weight = max(0.0, weight - s.strength * 0.3)
            modified.append({**b, "weight": round(weight, 3)})
        return modified

    def mark_failure(self, sigil_id: str):
        """
        Call this when Dex gets corrected.
        After threshold, sigil is ready to mutate.
        """
        for s in self.sigils:
            if s.id == sigil_id:
                s.failure_count += 1
                if s.failure_count >= 3:
                    # Suggest mutation — caller decides new name
                    return s
        return None

    def show(self):
        if not self.sigils:
            print("No sigils in memory.")
            return
        for s in self.sigils:
            print(s)

    def summary(self) -> dict:
        """Returns sigil state summary for dex_digest / longmind."""
        return {
            "total": len(self.sigils),
            "active": len([s for s in self.sigils if s.strength > 0.5]),
            "locked": len([s for s in self.sigils if s.mode == "LOCK"]),
            "sigils": [str(s) for s in self.sigils],
            "bridge_active": BRIDGE_ACTIVE,
        }
