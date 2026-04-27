"""
ReasonFlow Public API Contract

This is the stable interface guaranteed for v0.x releases.
Do not break these signatures.
"""

from typing import Callable, Any, Dict


TraceResult = Dict[str, Any]


def trace(func: Callable) -> Callable:
    """
    Decorator:
    - input: function(prompt)
    - output: TraceResult (dict)
    """
    ...
