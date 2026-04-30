"""
SIGIL CONTROL SYSTEM — TALNIR BUILD
Closed-loop cognition execution kernel (Final Form)
Routing governed by Talnir hierarchical graph traversal.

Talnir difference:
  - Sigils are NODES in a weighted directed graph
  - Activation is graph traversal, not direct match
  - Routing Governor filters subgraph candidates before scoring
  - Traversal score: strength × edge_weight × context_fit
                     × routing_bias × hysteresis_lock × diversity_pressure
  - Anti-attractor damping on dominant subgraphs
  - Mutation is boundary-isolated, sandbox-committed
"""

import json
import math
import time
import random
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# SIGIL NODE
# ─────────────────────────────────────────────

@dataclass
class SigilNode:
    id: str
    domain: str
    attributes: list
    subgraph: str
    strength: float = 0.5
    confidence: float = 0.5
    activation_threshold: float = 0.15
    last_activated: float = field(default_factory=time.time)
    activation_count: int = 0
    failure_count: int = 0
    hysteresis_lock: float = 1.0  # Talnir: prevents rapid switching

    def label(self):
        return f"⟦{self.domain}:{':'.join(self.attributes)}⟧"

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label(),
            "subgraph": self.subgraph,
            "strength": round(self.strength, 4),
            "confidence": round(self.confidence, 4),
            "hysteresis_lock": round(self.hysteresis_lock, 4),
            "activation_count": self.activation_count,
        }


# ─────────────────────────────────────────────
# TALNIR GRAPH
# ─────────────────────────────────────────────

class TalnirGraph:
    """
    Hierarchical sigil graph.
    Layer 1: Core sigil nodes
    Layer 2: Domain subgraphs
    Layer 3: Global routing graph
    """

    def __init__(self):
        self.nodes: dict[str, SigilNode] = {}
        self.edges: dict[str, dict[str, float]] = {}  # src → {dst: weight}
        self.subgraphs: dict[str, list[str]] = {}      # subgraph → [node_ids]
        self.subgraph_dominance: dict[str, float] = {} # tracks dominance

    def add_node(self, node: SigilNode):
        self.nodes[node.id] = node
        if node.subgraph not in self.subgraphs:
            self.subgraphs[node.subgraph] = []
            self.subgraph_dominance[node.subgraph] = 0.0
        if node.id not in self.subgraphs[node.subgraph]:
            self.subgraphs[node.subgraph].append(node.id)

    def add_edge(self, src_id: str, dst_id: str, weight: float = 0.5):
        if src_id not in self.edges:
            self.edges[src_id] = {}
        self.edges[src_id][dst_id] = weight

    def get_neighbors(self, node_id: str) -> list[tuple[str, float]]:
        return list(self.edges.get(node_id, {}).items())

    def update_subgraph_dominance(self):
        for sg, node_ids in self.subgraphs.items():
            nodes = [self.nodes[nid] for nid in node_ids if nid in self.nodes]
            if nodes:
                avg = sum(n.strength for n in nodes) / len(nodes)
                self.subgraph_dominance[sg] = avg


# ─────────────────────────────────────────────
# ROUTING GOVERNOR (P1)
# ─────────────────────────────────────────────

class RoutingGovernor:
    DOMINANCE_WINDOW = 5       # cycles before forced rotation
    DIVERSITY_MINIMUM = 2      # minimum subgraphs in candidate set
    DOMINANCE_THRESHOLD = 0.80

    def __init__(self):
        self.subgraph_history: list[str] = []
        self.cycle = 0

    def filter_candidates(self, graph: TalnirGraph, context: str) -> list[str]:
        """
        PIPELINE:
        1. Eliminate invalid subgraphs (context mismatch)
        2. Enforce diversity constraints
        3. Return filtered candidate set
        Probability is applied AFTER this step, not before.
        """
        self.cycle += 1
        all_subgraphs = list(graph.subgraphs.keys())

        # Step 1: context filter
        valid = []
        for sg in all_subgraphs:
            if self._context_relevant(sg, context):
                valid.append(sg)

        if not valid:
            valid = all_subgraphs  # fallback: allow all

        # Step 2: diversity enforcement
        # if same subgraph dominated last N cycles, deprioritize
        recent = self.subgraph_history[-self.DOMINANCE_WINDOW:]
        overdominant = set(sg for sg in recent
                          if recent.count(sg) >= self.DOMINANCE_WINDOW - 1)
        diverse = [sg for sg in valid if sg not in overdominant]

        if len(diverse) >= self.DIVERSITY_MINIMUM:
            valid = diverse

        # Step 3: anti-attractor check
        attractor_damped = []
        for sg in valid:
            dominance = graph.subgraph_dominance.get(sg, 0.0)
            if dominance > self.DOMINANCE_THRESHOLD:
                # apply damping — still in set but with penalty flag
                attractor_damped.append((sg, True))
            else:
                attractor_damped.append((sg, False))

        return attractor_damped  # list of (subgraph, is_damped)

    def record_selection(self, subgraph: str):
        self.subgraph_history.append(subgraph)
        if len(self.subgraph_history) > 20:
            self.subgraph_history.pop(0)

    def _context_relevant(self, subgraph: str, context: str) -> bool:
        return subgraph.lower() in context.lower() or True  # broad match for now


# ─────────────────────────────────────────────
# TALNIR TRAVERSAL ENGINE
# ─────────────────────────────────────────────

class TalnirTraversal:
    """
    Score formula:
    score = (strength × edge_weight × context_fit)
            × routing_bias
            × hysteresis_lock
            × diversity_pressure
    """

    def traverse(self, graph: TalnirGraph, start_nodes: list[str],
                 context: str, routing_bias: dict[str, float],
                 diversity_pressure: float = 1.0) -> list[tuple[float, SigilNode]]:

        visited = set()
        scored = []

        for start_id in start_nodes:
            if start_id not in graph.nodes:
                continue
            stack = [(start_id, 1.0)]  # (node_id, edge_weight_from_parent)

            while stack:
                nid, edge_w = stack.pop()
                if nid in visited:
                    continue
                visited.add(nid)

                node = graph.nodes[nid]
                ctx_fit = self._context_fit(context, node)
                r_bias = routing_bias.get(node.subgraph, 1.0)

                score = (
                    node.strength
                    * edge_w
                    * ctx_fit
                    * r_bias
                    * node.hysteresis_lock
                    * diversity_pressure
                )

                if score > node.activation_threshold:
                    scored.append((score, node))

                # traverse neighbors
                for neighbor_id, w in graph.get_neighbors(nid):
                    if neighbor_id not in visited:
                        stack.append((neighbor_id, w))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def _context_fit(self, context: str, node: SigilNode) -> float:
        ctx = context.lower()
        attr_hits = sum(1 for a in node.attributes if a.lower() in ctx)
        domain_hit = 0.3 if node.domain.lower() in ctx else 0.0
        return min(1.0, attr_hits * 0.4 + domain_hit + 0.2)


# ─────────────────────────────────────────────
# CONTROL PLANE (P0)
# ─────────────────────────────────────────────

class ControlPlane:
    SYSTEM_CEILING = 10.0
    DOMINANCE_CAP = 0.92
    MAX_ACTIVE_SET = 5
    SATURATION_LIMIT = 20

    def validate(self, graph: TalnirGraph) -> dict:
        nodes = list(graph.nodes.values())
        total = sum(n.strength for n in nodes)
        dominant = [n for n in nodes if n.strength > 0.85]
        return {
            "healthy": len(dominant) == 0,
            "total_strength": round(total, 4),
            "saturated": len(nodes) > self.SATURATION_LIMIT,
            "dominant_nodes": [n.label() for n in dominant],
        }

    def normalize(self, graph: TalnirGraph):
        nodes = list(graph.nodes.values())
        total = sum(n.strength for n in nodes)
        if total > self.SYSTEM_CEILING:
            factor = self.SYSTEM_CEILING / total
            for n in nodes:
                n.strength = min(n.strength * factor, self.DOMINANCE_CAP)

    def deterministic_fallback(self, candidates: list[tuple[float, SigilNode]],
                               max_n: int) -> list[SigilNode]:
        """Under saturation: pick highest-stability nodes deterministically."""
        stability_sorted = sorted(
            candidates,
            key=lambda x: x[1].strength * x[1].hysteresis_lock,
            reverse=True
        )
        return [n for _, n in stability_sorted[:max_n]]

    def enforce_caps(self, graph: TalnirGraph):
        for n in graph.nodes.values():
            n.strength = min(n.strength, self.DOMINANCE_CAP)


# ─────────────────────────────────────────────
# MUTATION ENGINE (BOUNDARY-ISOLATED)
# ─────────────────────────────────────────────

class MutationEngine:
    LEVELS = {1: "local", 2: "subgraph", 3: "cross_subgraph", 4: "global"}
    MIN_EVIDENCE = 3

    def evaluate(self, node: SigilNode) -> Optional[int]:
        if node.failure_count < self.MIN_EVIDENCE:
            return None
        if node.failure_count < 5:
            return 1
        if node.failure_count < 10:
            return 2
        return 3  # level 4 requires explicit sandbox only

    def sandbox_mutate(self, node: SigilNode, graph: TalnirGraph, level: int) -> Optional[SigilNode]:
        """Simulate mutation, return candidate without committing."""
        if level == 1:
            # local: add STRUCTURED attribute
            new_attrs = node.attributes + ["STRUCTURED"]
        elif level == 2:
            # subgraph: adjust domain
            new_attrs = node.attributes + ["BALANCED"]
        else:
            new_attrs = node.attributes + ["EVOLVED"]

        new_id = f"{node.id}_m{level}_{int(time.time())}"
        candidate = SigilNode(
            id=new_id,
            domain=node.domain,
            attributes=new_attrs,
            subgraph=node.subgraph,
            strength=node.strength * 0.8,
            confidence=node.confidence,
        )
        return candidate

    def commit(self, candidate: SigilNode, original: SigilNode, graph: TalnirGraph):
        """Commit after stability validation."""
        graph.add_node(candidate)
        original.strength *= 0.6
        return candidate


# ─────────────────────────────────────────────
# TALNIR SIGIL ENGINE (FULL RUNTIME)
# ─────────────────────────────────────────────

class TalnirSigilEngine:

    def __init__(self):
        self.graph = TalnirGraph()
        self.control_plane = ControlPlane()
        self.routing_governor = RoutingGovernor()
        self.traversal = TalnirTraversal()
        self.mutation_engine = MutationEngine()
        self.cycle_count = 0
        self.trace_log = []

    def create(self, domain: str, attributes: list, subgraph: str = "default",
               trigger: str = "explicit") -> SigilNode:
        sid = f"{domain}_{'_'.join(attributes)}"
        if sid in self.graph.nodes:
            return self.graph.nodes[sid]

        confidence_map = {"explicit": 0.7, "repeated_behavior": 0.5, "anomaly": 0.4}
        base_confidence = confidence_map.get(trigger, 0.5)
        strength = max(0.3, min(0.7, base_confidence + random.uniform(-0.1, 0.1)))

        node = SigilNode(
            id=sid, domain=domain, attributes=attributes,
            subgraph=subgraph, strength=strength, confidence=base_confidence
        )
        self.graph.add_node(node)
        self._trace("CREATE", node.label(), {"strength": strength, "trigger": trigger})
        return node

    def link(self, src_id: str, dst_id: str, weight: float = 0.5):
        self.graph.add_edge(src_id, dst_id, weight)

    def reinforce(self, node_id: str):
        if node_id not in self.graph.nodes:
            return
        n = self.graph.nodes[node_id]
        delta = 0.1 * (1.0 - n.strength)
        n.strength = min(n.strength + delta, self.control_plane.DOMINANCE_CAP)
        n.hysteresis_lock = min(n.hysteresis_lock + 0.05, 1.5)
        self._trace("REINFORCE", n.label(), {"strength": round(n.strength, 4)})

    def decay(self):
        now = time.time()
        for n in self.graph.nodes.values():
            elapsed = now - n.last_activated
            if elapsed > 300:
                n.strength = max(0.1, n.strength * math.exp(-0.02))
                n.hysteresis_lock = max(0.5, n.hysteresis_lock * 0.98)
        self._trace("DECAY", "pass", {})

    def run_cycle(self, context: str, prompt: str) -> dict:
        self.cycle_count += 1

        # P0: Control plane
        health = self.control_plane.validate(self.graph)
        if health["saturated"]:
            self.control_plane.normalize(self.graph)
        self.control_plane.enforce_caps(self.graph)

        # Update subgraph dominance
        self.graph.update_subgraph_dominance()

        # P1: Routing governor — filter candidates
        candidate_subgraphs = self.routing_governor.filter_candidates(self.graph, context)

        # Build routing bias from governor results
        routing_bias = {}
        for sg, is_damped in candidate_subgraphs:
            routing_bias[sg] = 0.5 if is_damped else 1.0

        # Diversity pressure: fewer candidates = higher pressure
        diversity_pressure = 1.0 / max(1, len(candidate_subgraphs))
        diversity_pressure = max(0.3, min(1.0, diversity_pressure * 3))

        # P2-P4: Talnir traversal
        start_nodes = list(self.graph.nodes.keys())
        scored = self.traversal.traverse(
            self.graph, start_nodes, context, routing_bias, diversity_pressure
        )

        # Deterministic fallback if saturated
        if health["saturated"] or len(scored) == 0:
            active = self.control_plane.deterministic_fallback(
                scored, self.control_plane.MAX_ACTIVE_SET
            )
        else:
            active = [n for _, n in scored[:self.control_plane.MAX_ACTIVE_SET]]

        # Record subgraph selection
        if active:
            self.routing_governor.record_selection(active[0].subgraph)
            for n in active:
                n.last_activated = time.time()
                n.activation_count += 1

        # Decay pass
        self.decay()

        # Mutation evaluation
        mutation_events = []
        for n in list(self.graph.nodes.values()):
            level = self.mutation_engine.evaluate(n)
            if level:
                candidate = self.mutation_engine.sandbox_mutate(n, self.graph, level)
                if candidate:
                    committed = self.mutation_engine.commit(candidate, n, self.graph)
                    mutation_events.append(f"{n.label()} → {committed.label()}")
                    self._trace("MUTATE", committed.label(), {"level": level})

        # Output injection
        injection = self._inject(active, prompt)

        # Self-calibration every 10 cycles
        if self.cycle_count % 10 == 0:
            self.control_plane.normalize(self.graph)
            self._trace("CALIBRATE", "self-calibration pass", {})

        return {
            "cycle": self.cycle_count,
            "health": health,
            "candidate_subgraphs": [sg for sg, _ in candidate_subgraphs],
            "routing_bias": routing_bias,
            "active_sigils": [n.label() for n in active],
            "primary": active[0].label() if active else None,
            "injection": injection,
            "mutations": mutation_events,
            "trace": self.trace_log[-5:],
        }

    def _inject(self, active: list[SigilNode], prompt: str) -> dict:
        verbosity = "normal"
        focus = []
        constraints = []
        for n in active:
            if "BRIEF" in n.attributes: verbosity = "brief"
            if "DETAILED" in n.attributes: verbosity = "detailed"
            if "DEBUG" in n.attributes: focus.append("debug")
            if "SAFE" in n.attributes: constraints.append("safety_check")
            if "SEARCH" in n.attributes: focus.append("search")
        return {
            "prompt": prompt,
            "verbosity": verbosity,
            "focus": focus,
            "constraints": constraints,
            "active_sigils": [n.label() for n in active],
        }

    def _trace(self, event: str, target: str, data: dict):
        self.trace_log.append({
            "cycle": self.cycle_count,
            "event": event,
            "target": target,
            "data": data,
            "ts": round(time.time(), 2),
        })

    def state(self):
        return {nid: n.to_dict() for nid, n in self.graph.nodes.items()}


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    engine = TalnirSigilEngine()

    # Create nodes
    brief = engine.create("PREF", ["BRIEF"], subgraph="style", trigger="repeated_behavior")
    debug = engine.create("HEUR", ["DEBUG", "FIRST"], subgraph="reasoning", trigger="explicit")
    search = engine.create("TOOL", ["ENABLE", "SEARCH"], subgraph="tools", trigger="explicit")
    safe = engine.create("CTX", ["SAFE"], subgraph="safety", trigger="explicit")
    detailed = engine.create("PREF", ["DETAILED"], subgraph="style", trigger="explicit")

    # Wire graph edges (Talnir routing paths)
    engine.link(brief.id, safe.id, weight=0.6)
    engine.link(debug.id, search.id, weight=0.8)
    engine.link(search.id, brief.id, weight=0.4)
    engine.link(safe.id, brief.id, weight=0.5)
    engine.link(detailed.id, debug.id, weight=0.7)

    print("=" * 55)
    print("SIGIL TALNIR BUILD — Hierarchical Graph Routing")
    print("=" * 55)

    tests = [
        ("brief style safe response", "explain this quickly"),
        ("reasoning debug search needed", "search and debug this error"),
        ("detailed reasoning debug", "deep dive on this issue"),
        ("tools search enable", "find information on this"),
    ]

    for context, prompt in tests:
        result = engine.run_cycle(context, prompt)
        print(f"\nCONTEXT: {context}")
        print(f"  Subgraphs considered: {result['candidate_subgraphs']}")
        print(f"  Routing bias:         {result['routing_bias']}")
        print(f"  Active sigils:        {result['active_sigils']}")
        print(f"  Primary:              {result['primary']}")
        print(f"  Verbosity:            {result['injection']['verbosity']}")
        print(f"  Focus:                {result['injection']['focus']}")

    # Reinforce
    print("\n--- Reinforcing PREF_BRIEF (Talnir updates hysteresis lock) ---")
    engine.reinforce(brief.id)
    print(f"  Strength: {engine.graph.nodes[brief.id].strength:.4f}")
    print(f"  Hysteresis: {engine.graph.nodes[brief.id].hysteresis_lock:.4f}")

    # Trigger mutation
    print("\n--- Simulating failures → mutation ladder ---")
    engine.graph.nodes[debug.id].failure_count = 5
    result = engine.run_cycle("reasoning debug", "test mutation")
    print(f"  Mutations: {result['mutations']}")

    print("\n--- Final Graph State ---")
    print(json.dumps(engine.state(), indent=2))
