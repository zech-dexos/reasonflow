# ReasonFlow

ReasonFlow turns every LLM call into a fully explainable reasoning trace with persistent behavioral memory.

---

## The Problem

LLMs give answers, but developers cannot reliably see:
- why a decision was made
- what influenced it
- how behavior changes over time

ReasonFlow makes reasoning visible and persistent.

---## Quick Start

Install:
    pip install reasonflow

Run:
    from reasonflow.engine import run
    result = run("debug this login function")
    print(result)

Example output:

    INPUT: debug this login function
    CONTEXT: CTX:CODING

    SIGILS ACTIVE:
      [HEUR:DEBUG_FIRST] s=0.76  biases toward debugging
      [PREF:BRIEF]       s=0.66  prefers concise output

    BRANCHES:
      direct       0.700
      structured   1.000  <- selected
      exploratory  0.600
      debug_first  0.652  <- biased up by DEBUG_FIRST sigil

    OUTPUT: structured reasoning about the login bug

    TRACE ID: a3f2c1b4
    DECISION EXPLAINED.

---
## What Sigils Are

Sigils are behavioral memory, not stored facts.

They do not store what happened.
They store how the system should think because of what happened.

Examples:
  [PREF:BRIEF]           prefer short answers
  [HEUR:DEBUG_FIRST]     prioritize debugging reasoning
  [RISK:NO_ASSUMPTIONS]  penalize unsupported inference

Sigils strengthen when behavior is confirmed.
Sigils decay when unused.
Sigils mutate when outcomes contradict expectations.

This is not memory retrieval.
This is probability shaping over reasoning structure.

---
## Sigil Lifecycle

CREATE    - repeated behavior or explicit instruction
ACTIVATE  - context match triggers the sigil
REINFORCE - correct outcome increases strength
DECAY     - unused sigils weaken over time
MUTATE    - contradictory outcomes reshape the sigil
EMERGE    - new sigils created from trace patterns

---
## The Full Pipeline

INPUT PROMPT
    -> CONTEXT DETECTION
    -> SIGIL ACTIVATION
    -> BRANCH GENERATION
    -> SIGIL BIAS APPLIED TO BRANCHES
    -> BRANCH SELECTION
    -> EXECUTION
    -> FULL TRACE OUTPUT
    -> MEMORY UPDATE
    (loops back)

---
## Core Guarantee

Every run() returns:
- input prompt
- active sigils with strength scores
- generated branches with weights
- selected branch and reason
- final output
- trace ID

No hidden reasoning. Ever.

---

## One-Line Definition

ReasonFlow is a symbolic reasoning trace system where
memory shapes decision-making through behavioral sigils.

---

Built by Zech (Root) — solo, local hardware, no team.
Part of the DexOS sovereign AI project.
