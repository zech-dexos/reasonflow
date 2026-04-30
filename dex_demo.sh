#!/bin/bash
# ─────────────────────────────────────────────────────────────
# DexOS Demo — One Clean Path
# Shows: NL input → Talnir translate → sigil routing → 
#        brain selection → memory write → trace visible
#
# Run: bash dex_demo.sh
# ─────────────────────────────────────────────────────────────

set -e

REASONFLOW_DIR="$HOME/reasonflow"
MEMORY_FILE="$HOME/.reasonflow/dex_memory.jsonl"
SIGIL_FILE="$HOME/.reasonflow/sigils.json"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
DIM='\033[2m'
RESET='\033[0m'

divider() {
    echo -e "${DIM}────────────────────────────────────────────────────${RESET}"
}

header() {
    echo ""
    echo -e "${WHITE}$1${RESET}"
    divider
}

# ─────────────────────────────────────────────
# STEP 0: SYSTEM CHECK
# ─────────────────────────────────────────────
header "☩ DexOS — ReasonFlow Demo"
echo -e "${DIM}A locally-running AI system with identity, memory, and behavioral routing.${RESET}"
echo ""

echo -e "${CYAN}[0] System check${RESET}"
echo -n "    ollama server: "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}running ✓${RESET}"
else
    echo -e "${YELLOW}not running — starting...${RESET}"
    ollama serve &>/dev/null &
    sleep 2
fi

echo -n "    dex model: "
if ollama list 2>/dev/null | grep -q "dex"; then
    echo -e "${GREEN}loaded ✓${RESET}"
else
    echo -e "${YELLOW}not found (using llama3.1)${RESET}"
fi

echo -n "    memory file: "
if [ -f "$MEMORY_FILE" ]; then
    LINES=$(wc -l < "$MEMORY_FILE")
    echo -e "${GREEN}${LINES} events ✓${RESET}"
else
    echo -e "${DIM}empty (will be created)${RESET}"
    mkdir -p "$(dirname $MEMORY_FILE)"
fi

# ─────────────────────────────────────────────
# STEP 1: SHOW ACTIVE SIGILS
# ─────────────────────────────────────────────
header "[1] Active Sigil State"
if [ -f "$SIGIL_FILE" ]; then
    python3 -c "
import json
data = json.load(open('$SIGIL_FILE'))
if not data:
    print('  No sigils yet.')
else:
    for s in data:
        bar = '█' * int(s['strength'] * 10)
        print(f\"  [{s['type']}:{s['name']}:{s['mode']}] strength={s['strength']:.2f} {bar}\")
"
else
    echo -e "  ${DIM}No sigils yet.${RESET}"
fi

# ─────────────────────────────────────────────
# STEP 2: TALNIR TRANSLATION DEMO
# ─────────────────────────────────────────────
header "[2] Talnir Translator — NL → Structured Signal"
echo -e "${DIM}Input:${RESET} \"debug why my python script crashes on import\""
echo ""

cd "$REASONFLOW_DIR"
python3 -c "
import sys
sys.path.insert(0, '.')
from reasonflow.talnir import translate

prompts = [
    'debug why my python script crashes on import',
    'write a function to parse JSON safely',
    'quickly explain what a sigil is',
    'run the test suite and fix any failures',
]
for p in prompts:
    s = translate(p)
    print(f'  IN:  {p}')
    print(f'  OUT: intent={s.intent} | domain={s.domain} | mods={s.modifiers} | tools={s.tools}')
    print(f'       context_string: {s.to_context_string()}')
    print()
"

# ─────────────────────────────────────────────
# STEP 3: FULL REASONFLOW CYCLE (LIVE)
# ─────────────────────────────────────────────
header "[3] Live ReasonFlow Cycle"
DEMO_PROMPT="debug why my python script crashes on import"
echo -e "${DIM}Prompt:${RESET} \"$DEMO_PROMPT\""
echo ""

python3 -c "
import sys, json
sys.path.insert(0, '.')
from reasonflow.engine import run

trace = run('$DEMO_PROMPT')

print(f'  signal:    {trace[\"signal\"]}')
print(f'  context:   {trace[\"context\"]}')
print(f'  sigils:    {trace[\"active_sigils\"] or \"(none active yet)\"}')

branches = sorted(trace['branches'], key=lambda b: b['weight'], reverse=True)
print(f'  branches:')
for b in branches:
    bar = '▓' * int(b['weight'] * 10)
    print(f'    {b[\"id\"]:20s} {b[\"weight\"]:.2f} {bar}')

print(f'  selected:  {trace[\"selected\"][\"id\"]}')
print(f'  brain:     {trace[\"specialized_model\"] or \"default (no specialized brain needed)\"}')
print()
if trace['preprocessed']:
    print(f'  preprocessed output:')
    lines = trace['preprocessed'].split('\n')
    for line in lines[:3]:
        if line.strip():
            print(f'    {line.strip()}')
"

# ─────────────────────────────────────────────
# STEP 4: MEMORY TRACE
# ─────────────────────────────────────────────
header "[4] Memory — What Dex Just Wrote"
if [ -f "$MEMORY_FILE" ]; then
    echo -e "${DIM}Last 3 entries in dex_memory.jsonl:${RESET}"
    tail -3 "$MEMORY_FILE" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line.strip())
        print(f'  [{e.get(\"event\",\"?\")}] {e.get(\"sigil\", e.get(\"selected_branch\", \"\"))} @ ts={e.get(\"ts\",\"?\")}')
    except: pass
"
else
    echo -e "  ${DIM}Memory file not yet created.${RESET}"
fi

# ─────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────
echo ""
divider
echo -e "${GREEN}Demo complete.${RESET}"
echo ""
echo -e "  What you just saw:"
echo -e "  • Natural language → Talnir structured signal (rule-based, deterministic)"
echo -e "  • Signal → branch routing → specialized brain selection"
echo -e "  • Sigil behavioral layer biases the routing"
echo -e "  • Every cycle writes to dex_memory.jsonl"
echo -e "  • All running locally on llama3.1 via single ollama server"
echo ""
echo -e "  ${DIM}github.com/zech-dexos/reasonflow${RESET}"
echo ""
