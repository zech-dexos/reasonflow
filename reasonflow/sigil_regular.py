"""
SIGIL CONTROL SYSTEM — REGULAR BUILD
Closed-loop cognition execution kernel (Final Form)
No Talnir routing. Direct lifecycle management.
"""

import json
import math
import time
import random
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# SIGIL DATA STRUCTURE
# ─────────────────────────────────────────────

@dataclass
class Sigil:
    id: str
    domain: str           # PREF, HEUR, CTX, TOOL, etc.
    attributes: list
    strength: float = 0.5
    confidence: float = 0.5
    activation_threshold: float = 0.15
    last_activated: float = field(default_factory=time.time)
    activation_count: int = 0
    failure_count: int = 0
    subgraph: str = "default"

    def label(self):
        return f"⟦{self.domain}:{':'.join(self.attributes)}⟧"

    def to_dict(self):
        return {
            "id": self.id,
            "domain": self.domain,
            "attributes": self.attributes,
            "strength": round(self.strength, 4),
            "confidence": round(self.confidence, 4),
            "subgraph": self.subgraph,
            "activation_count": self.activation_count,
        }


# ─────────────────────────────────────────────
# SIGIL GOVERNOR (P0 — ABSOLUTE AUTHORITY)
# ─────────────────────────────────────────────

class SigilGovernor:
    DOMINANCE_CAP = 0.92
    SYSTEM_STRENGTH_CEILING = 10.0
    MAX_ACTIVE_SET = 5

    def normalize(self, sigils: list[Sigil]):
        total = sum(s.strength for s in sigils)
        if total > self.SYSTEM_STRENGTH_CEILING:
            factor = self.SYSTEM_STRENGTH_CEILING / total
            for s in sigils:
                s.strength *= factor

    def enforce_dominance_cap(self, sigils: list[Sigil]):
        for s in sigils:
            if s.strength > self.DOMINANCE_CAP:
                s.strength = self.DOMINANCE_CAP

    def get_active_set(self, candidates: list[Sigil]) -> list[Sigil]:
        sorted_candidates = sorted(candidates, key=lambda s: s.strength, reverse=True)
        return sorted_candidates[:self.MAX_ACTIVE_SET]

    def validate_health(self, sigils: list[Sigil]) -> dict:
        total_strength = sum(s.strength for s in sigils)
        dominant = [s for s in sigils if s.strength > 0.85]
        return {
            "healthy": len(dominant) == 0 and total_strength < self.SYSTEM_STRENGTH_CEILING,
            "total_strength": round(total_strength, 4),
            "dominant_sigils": [s.label() for s in dominant],
            "saturation": len(sigils) > 20
        }


# ─────────────────────────────────────────────
# LIFECYCLE ENGINE
# ─────────────────────────────────────────────

class SigilEngine:
    DECAY_RATE = 0.02
    DECAY_FLOOR = 0.1
    DECAY_WINDOW = 300  # seconds

    def __init__(self):
        self.sigils: dict[str, Sigil] = {}
        self.governor = SigilGovernor()
        self.cycle_count = 0
        self.trace_log = []

    # 1. CREATION
    def create(self, domain: str, attributes: list, subgraph: str = "default",
               trigger: str = "explicit") -> Sigil:
        sid = f"{domain}_{':'.join(attributes)}".replace(":", "_")
        if sid in self.sigils:
            return self.sigils[sid]

        confidence_map = {
            "explicit": 0.7,
            "repeated_behavior": 0.5,
            "anomaly": 0.4,
        }
        base_confidence = confidence_map.get(trigger, 0.5)

        # bounded initialization
        strength = max(0.3, min(0.7, base_confidence + random.uniform(-0.1, 0.1)))

        s = Sigil(
            id=sid,
            domain=domain,
            attributes=attributes,
            strength=strength,
            confidence=base_confidence,
            subgraph=subgraph,
        )
        self.sigils[sid] = s
        self._trace("CREATE", s.label(), {"strength": strength, "trigger": trigger})
        return s

    # 2. ACTIVATION
    def activate(self, context: str) -> list[Sigil]:
        now = time.time()
        activated = []
        for s in self.sigils.values():
            recency = math.exp(-(now - s.last_activated) / 600)
            context_match = self._context_match(context, s)
            weight = s.strength * context_match * recency
            if weight > s.activation_threshold:
                s.last_activated = now
                s.activation_count += 1
                s.strength = min(s.strength + 0.02, self.governor.DOMINANCE_CAP)
                activated.append((weight, s))

        activated.sort(key=lambda x: x[0], reverse=True)
        active_sigils = self.governor.get_active_set([s for _, s in activated])
        self._trace("ACTIVATE", f"{len(active_sigils)} sigils", {"context": context[:40]})
        return active_sigils

    # 3. REINFORCEMENT
    def reinforce(self, sigil_id: str):
        if sigil_id not in self.sigils:
            return
        s = self.sigils[sigil_id]
        # diminishing returns curve
        delta = 0.1 * (1.0 - s.strength)
        s.strength = min(s.strength + delta, self.governor.DOMINANCE_CAP)
        s.confidence = min(s.confidence + 0.05, 1.0)
        self._trace("REINFORCE", s.label(), {"new_strength": round(s.strength, 4)})

    # 4. DECAY
    def decay(self):
        now = time.time()
        for s in self.sigils.values():
            elapsed = now - s.last_activated
            if elapsed > self.DECAY_WINDOW:
                s.strength = max(
                    self.DECAY_FLOOR,
                    s.strength * math.exp(-self.DECAY_RATE)
                )
        self._trace("DECAY", "pass", {})

    # 5. CONFLICT RESOLUTION
    def resolve_conflict(self, competing: list[Sigil], context: str) -> Sigil:
        now = time.time()
        scores = []
        for s in competing:
            recency = math.exp(-(now - s.last_activated) / 600)
            ctx_match = self._context_match(context, s)
            score = s.strength * ctx_match * recency
            scores.append((score, s))

        scores.sort(key=lambda x: x[0], reverse=True)
        winner_score, winner = scores[0]

        # absolute winner only if above dominance threshold
        if winner_score > 0.75:
            return winner

        # weighted probabilistic vote otherwise
        total = sum(sc for sc, _ in scores)
        pick = random.uniform(0, total)
        cumulative = 0
        for sc, s in scores:
            cumulative += sc
            if cumulative >= pick:
                return s
        return winner

    # 6. MUTATION
    def mutate(self, sigil_id: str, level: int = 1):
        if sigil_id not in self.sigils:
            return None
        s = self.sigils[sigil_id]
        if s.failure_count < 3:
            return None  # minimum evidence threshold

        # preserve semantic lineage
        if level == 1:
            # local: add STRUCTURED attribute
            new_attrs = s.attributes + ["STRUCTURED"]
            new_id = f"{s.domain}_{'_'.join(new_attrs)}"
            mutated = Sigil(
                id=new_id,
                domain=s.domain,
                attributes=new_attrs,
                strength=s.strength * 0.8,
                confidence=s.confidence,
                subgraph=s.subgraph,
            )
            self.sigils[new_id] = mutated
            # original weakens
            s.strength *= 0.6
            self._trace("MUTATE", f"{s.label()} → {mutated.label()}", {"level": level})
            return mutated
        return None

    # 7. OUTPUT INJECTION
    def inject(self, active: list[Sigil], prompt: str) -> dict:
        verbosity = "normal"
        focus = []
        constraints = []

        for s in active:
            if "BRIEF" in s.attributes:
                verbosity = "brief"
            if "DETAILED" in s.attributes:
                verbosity = "detailed"
            if "DEBUG" in s.attributes:
                focus.append("debug")
            if "SAFE" in s.attributes:
                constraints.append("safety_check")

        return {
            "prompt": prompt,
            "verbosity": verbosity,
            "focus": focus,
            "constraints": constraints,
            "active_sigils": [s.label() for s in active],
        }

    # SELF-CALIBRATION
    def calibrate(self):
        self.governor.normalize(list(self.sigils.values()))
        self.governor.enforce_dominance_cap(list(self.sigils.values()))
        self._trace("CALIBRATE", "pass", {"sigil_count": len(self.sigils)})

    # FULL EXECUTION LOOP
    def run_cycle(self, context: str, prompt: str) -> dict:
        self.cycle_count += 1

        # P0: Control plane health check
        health = self.governor.validate_health(list(self.sigils.values()))

        # Deterministic fallback if saturated
        if health["saturation"]:
            self.calibrate()

        # P1-P4: Activate and resolve
        active = self.activate(context)

        # Conflict resolution if competing
        if len(active) > 1:
            winner = self.resolve_conflict(active, context)
            primary = winner
        else:
            primary = active[0] if active else None

        # Decay pass
        self.decay()

        # Output injection
        injection = self.inject(active, prompt)

        # Rebalance
        if self.cycle_count % 10 == 0:
            self.calibrate()

        return {
            "cycle": self.cycle_count,
            "health": health,
            "active_sigils": [s.label() for s in active],
            "primary": primary.label() if primary else None,
            "injection": injection,
            "trace": self.trace_log[-5:],
        }

    # HELPERS
    def _context_match(self, context: str, sigil: Sigil) -> float:
        context_lower = context.lower()
        hits = sum(1 for attr in sigil.attributes if attr.lower() in context_lower)
        domain_hit = 0.3 if sigil.domain.lower() in context_lower else 0
        return min(1.0, (hits * 0.4) + domain_hit + 0.2)

    def _trace(self, event: str, target: str, data: dict):
        self.trace_log.append({
            "cycle": self.cycle_count,
            "event": event,
            "target": target,
            "data": data,
            "ts": round(time.time(), 2),
        })

    def state(self):
        return {s.id: s.to_dict() for s in self.sigils.values()}


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    engine = SigilEngine()

    # Seed some sigils
    engine.create("PREF", ["BRIEF"], subgraph="style", trigger="repeated_behavior")
    engine.create("HEUR", ["DEBUG", "FIRST"], subgraph="reasoning", trigger="explicit")
    engine.create("TOOL", ["ENABLE", "SEARCH"], subgraph="tools", trigger="explicit")
    engine.create("CTX", ["SAFE"], subgraph="safety", trigger="explicit")

    print("=" * 50)
    print("SIGIL REGULAR BUILD — Closed Loop Runtime")
    print("=" * 50)

    tests = [
        ("brief explanation needed", "explain this quickly"),
        ("debug mode search needed", "search and debug this error"),
        ("safe brief response", "quick safe answer please"),
    ]

    for context, prompt in tests:
        result = engine.run_cycle(context, prompt)
        print(f"\nCONTEXT: {context}")
        print(f"  Active:  {result['active_sigils']}")
        print(f"  Primary: {result['primary']}")
        print(f"  Inject:  verbosity={result['injection']['verbosity']}, focus={result['injection']['focus']}")

    # Test reinforcement
    print("\n--- Reinforcing PREF_BRIEF ---")
    engine.reinforce("PREF_BRIEF")
    print(f"New strength: {engine.sigils['PREF_BRIEF'].strength:.4f}")

    # Test mutation
    print("\n--- Simulating failure → mutation ---")
    engine.sigils["PREF_BRIEF"].failure_count = 4
    mutated = engine.mutate("PREF_BRIEF", level=1)
    if mutated:
        print(f"Mutated to: {mutated.label()}")

    print("\n--- Final State ---")
    print(json.dumps(engine.state(), indent=2))
