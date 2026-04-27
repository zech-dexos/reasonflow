import sys
from reasonflow.engine import run

def main():
    prompt = " ".join(sys.argv[1:])
    trace = run(prompt)

    print("\n=== REASONFLOW ===")
    print("INPUT:", trace["input"])

    print("\nBRANCHES:")
    for b in trace["branches"]:
        print(" -", b)

    print("\nSELECTED:", trace["selected"])
    print("\nOUTPUT:", trace["output"])
