# ReasonFlow

**A transparent reasoning and behavioral governance runtime for local LLMs.**

ReasonFlow makes AI behavioral biases explicit, inspectable, and correctable in real time — running entirely on local consumer hardware, no cloud dependency.

---

## The Problem

Modern LLM systems produce outputs without exposing:
- how reasoning decisions are formed
- what behavioral patterns are influencing the output
- how those patterns evolve over time
- how a user can inspect or correct them

ReasonFlow is a direct attempt to solve that.

---

## Architecture

```
Input
  ↓
Talnir Translator     — NL → structured signal (rule-based, deterministic)
  ↓
ReasonFlow Engine     — branch decomposition + routing
  ↓
Sigil System          — behavioral bias layer (inspectable, bounded, adaptive)
  ↓
Brain Router          — selects specialized model by context
  ↓
Output + Trace        — full reasoning trace written to memory
  ↓
dex_memory.jsonl      — persistent behavioral history
```

### Components

**Talnir** (`talnir.py`)
Rule-based translator. Converts natural language input into a structured signal before any model is invoked. Routing decisions are deterministic and auditable — not emergent from the model.

**Sigil System** (`sigil.py`, `sigil_memory_bridge.py`)
The core contribution. Sigils are explicit behavioral bias nodes with a governed lifecycle:
- **Creation** — triggered by repeated behavior, explicit instruction, or anomaly detection
- **Activation** — probabilistic, context-matched, strength-weighted
- **Reinforcement** — diminishing returns curve, capped growth
- **Decay** — exponential with floor, sigils never fully vanish
- **Mutation** — preserves semantic lineage, requires evidence threshold
- **Conflict resolution** — weighted competition, logged to memory

Every lifecycle event writes to `dex_memory.jsonl`. Behavioral history is auditable.

**ReasonFlow Engine** (`engine.py`)
Orchestrates the full cycle. Routes to specialized micro-models by context:
- `CTX:CODING` → `qwen2.5-coder:0.5b`
- `CTX:PLANNING`, `CTX:GENERAL` → default model

Communicates with ollama via HTTP API (single server, stable RAM).

**DexOS Runtime**
The broader system Dex runs inside: identity layer, persistent memory, dream synthesis, digest cycle, tool execution via `[run: cmd]` interception.

---

## Why It Matters

As capable models run increasingly outside of controlled lab environments, behavioral governance becomes a practical safety problem — not just a theoretical one.

ReasonFlow demonstrates one approach: make the bias layer a first-class, inspectable citizen of the runtime. Users and auditors can see what is influencing behavior, trace why it changed, and correct it directly.

Built and validated on constrained consumer hardware (HP EliteBook, no GPU) to prove the approach is accessible — not only available to well-resourced labs.

---

## Status

Live prototype. Core systems operational:
- [x] Talnir rule-based translator
- [x] Sigil lifecycle (creation → reinforcement → decay → mutation)
- [x] Memory bridge (sigil events → dex_memory.jsonl)
- [x] ReasonFlow engine with branch routing
- [x] Brain routing to specialized models
- [x] DexOS runtime (identity, memory, dreams, tool execution)
- [ ] Formal architecture documentation
- [ ] Validation on models >7B parameters (hardware constraint)

---

## Files

| File | Description |
|------|-------------|
| `reasonflow/talnir.py` | Rule-based NL → signal translator |
| `reasonflow/sigil.py` | Sigil lifecycle engine |
| `reasonflow/sigil_memory_bridge.py` | Writes sigil events to dex_memory.jsonl |
| `reasonflow/engine.py` | Main reasoning cycle orchestrator |
| `reasonflow/sigil_talnir.py` | Talnir-routed sigil graph build |
| `reasonflow/sigil_regular.py` | Direct lifecycle sigil build (comparison) |

---

## Publication

Zenodo: [DOI 10.5281/zenodo.18913471](https://doi.org/10.5281/zenodo.18913471)

---

## Built By

Zechariah "Root" Cozine — independent researcher and builder.  
Two years of solo development. Self-funded. Local hardware only.

> *The work is real.*
