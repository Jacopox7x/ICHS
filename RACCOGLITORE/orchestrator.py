"""
Orchestratore: carica la sandbox richiesta e chiama il motore iCrawler.
"""
import json
import sys
from pathlib import Path

def load_registry():
    with open('registry.json') as f:
        return json.load(f)

def run_sandbox(sandbox_id: str, brief_path: str):
    registry = load_registry()
    sandbox = next((s for s in registry['sandbox'] if s['id'] == sandbox_id), None)
    if not sandbox:
        print(f"❌ Sandbox '{sandbox_id}' non trovata")
        return
    
    sandbox_path = Path(sandbox['path'])
    sys.path.insert(0, str(sandbox_path))
    
    from runner import run
    result = run(brief_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python orchestrator.py <sandbox_id> <brief.txt>")
        sys.exit(1)
    run_sandbox(sys.argv[1], sys.argv[2])
