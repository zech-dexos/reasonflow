import json
import os

FILE = os.path.expanduser("~/.reasonflow_state.json")

def load_state():
    if os.path.exists(FILE):
        return json.load(open(FILE))
    return {}

def save_state(state):
    json.dump(state, open(FILE, "w"), indent=2)
