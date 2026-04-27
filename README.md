# ReasonFlow
ReasonFlow guarantees an **explainable trace for every AI decision**.
No black box reasoning. Every output is structured, inspectable, and reproducible.
---
## Core Guarantee
Every `ReasonFlow` run produces:
- the input prompt
- activated sigils (behavioral memory)
- generated reasoning branches
- the selected decision path
- the final output
This is always visible. Nothing is hidden.
---
## What Sigils Are
Sigils are **behavioral memory**, not stored facts.
They do not store what happened.
They store:
> how the system should think because of what happened
Example:
- `⟦PREF:BRIEF⟧` → prefer short answers
- `⟦HEUR:DEBUG_FIRST⟧` → prioritize debugging reasoning
- `⟦RISK:NO_ASSUMPTIONS⟧` → penalize unsupported inference
Sigils shape reasoning over time.
---
## What ReasonFlow Does
A ReasonFlow run always follows this loop:
1. Receive input
2. Load memory (sigils)
3. Activate relevant sigils
4. Build reasoning branches (graph)
5. Apply sigil bias to branches
6. Select best path
7. Execute output
8. Emit full trace
---
## Why It Matters
Traditional LLM systems:
- output answers
- hide reasoning
- forget why decisions changed
ReasonFlow:
- exposes reasoning paths
- explains every decision
- evolves behavior through sigils
- makes model behavior inspectable over time
---
## One-Line Definition
ReasonFlow is a **symbolic reasoning trace system where memory shapes decision-making through behavioral sigils.**
