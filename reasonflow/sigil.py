"""
Sigil System v1 — ReasonFlow Memory Layer
Author: Zech (Root) / Deximus Maximus
"""
import json, os, time, uuid
from dataclasses import dataclass, field, asdict

SIGIL_FILE = os.path.expanduser("~/.reasonflow/sigils.json")

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

    def __post_init__(self):
        if self.last_activated == 0.0:
            self.last_activated = self.created_at

    def activate(self):
        self.strength = min(1.0, self.strength + 0.05)
        self.last_activated = time.time()
        self.activation_count += 1

    def reinforce(self):
        self.strength = min(1.0, self.strength + 0.1)
        self.confidence = min(1.0, self.confidence + 0.05)

    def decay(self):
        if self.mode == "LOCK":
            return
        age = time.time() - self.last_activated
        if age > 3600:
            self.strength = max(0.0, self.strength - self.decay_rate)

    def mutate(self, new_name):
        self.name = new_name
        self.mode = "DRIFT"
        self.strength = max(0.3, self.strength - 0.1)

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
               context="CTX:ALL", strength=0.6):
        s = Sigil(type=type, name=name, mode=mode,
                  context=context, strength=strength)
        self.sigils.append(s)
        self.save()
        return s

    def activate_for_context(self, context):
        active = []
        for s in self.sigils:
            s.decay()
            score = s.score(context)
            if score > 0.1:
                s.activate()
                active.append(s)
        active.sort(key=lambda s: s.score(context), reverse=True)
        self.save()
        return active

    def resolve_conflicts(self, active, context):
        return sorted(active,
                      key=lambda s: s.score(context),
                      reverse=True)[:5]

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

    def show(self):
        if not self.sigils:
            print("No sigils in memory.")
            return
        for s in self.sigils:
            print(s)
