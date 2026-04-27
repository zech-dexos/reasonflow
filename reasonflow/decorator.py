from functools import wraps
from .engine import run


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        prompt = " ".join(str(a) for a in args)

        result = run(prompt)

        # stable output contract
        trace_obj = {
            "input": result["input"],
            "branches": result["branches"],
            "selected": result["selected"],
            "output": result["output"],
            "trace_id": result["trace_id"]
        }

        # optional human print (non-breaking)
        print("\n=== REASONFLOW TRACE ===")
        print("INPUT:", trace_obj["input"])

        print("\nBRANCHES:")
        for b in trace_obj["branches"]:
            mark = "← selected" if b["id"] == trace_obj["selected"]["id"] else ""
            print(f" - {b['id']} ({b['weight']}) {mark}")

        print("\nOUTPUT:", trace_obj["output"])
        print("========================\n")

        return trace_obj

    return wrapper
