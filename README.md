# ReasonFlow

Debug how your AI makes decisions — step by step.

---

## Install

pip install reasonflow

---

## Example

from reasonflow import trace

@trace
def ask_ai(prompt):
    return f"AI response to: {prompt}"

ask_ai("how do I design a login system?")

---

## Output

=== REASONFLOW TRACE ===
INPUT: how do I design a login system?

BRANCHES:
 - direct (0.7)
 - structured (1.0) ← selected
 - exploratory (0.6)

OUTPUT: [ReasonFlow Structured] how do I design a login system
========================

---

## Why ReasonFlow?

When working with AI systems, it's hard to understand:
- Why did the model choose this response?
- Why are outputs inconsistent?
- What reasoning path was taken?

ReasonFlow makes that visible.

---

## Use Cases
- Debug LLM behavior
- Understand prompt outcomes
- Build more reliable AI systems
