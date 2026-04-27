# ReasonFlow — Product Direction v1

## Core Product Definition
ReasonFlow is a deterministic reasoning execution layer for LLMs where every decision is traceable, explainable, and influenced by symbolic memory (sigils).

## Core Guarantee
Every run MUST output:
1. Input prompt
2. Active sigils (memory influence)
3. Generated reasoning branches
4. Selected branch
5. Final output
6. Full trace of decision process

No hidden reasoning paths allowed.

## Positioning
NOT: LangChain competitor, agent framework, orchestration library
IS: explainable AI execution layer, deterministic reasoning trace system, symbolic memory-influenced decision engine

## Success Criteria
- Install in under 1 minute
- Understand in under 30 seconds
- See exactly why every output happened
- Behavior is reproducible and inspectable

## Final Principle
ReasonFlow does not just produce answers.
It produces decisions with visible reasoning history, shaped by evolving symbolic memory.
