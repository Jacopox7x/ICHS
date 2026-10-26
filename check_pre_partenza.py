#!/usr/bin/env python3
"""Quality gate pre-generazione. Exit 0 = OK, 1 = DEGRADED, 2 = FAILED."""
import sys
import json
import subprocess
from pathlib import Path


def check_ollama():
    try:
        r = subprocess.run(
            ["curl", "-s", "--max-time", "2", "http://127.0.0.1:11434/api/tags"],
            capture_output=True, text=True, timeout=3
        )
        if r.returncode != 0 or not r.stdout.strip():
            return "FAILED", "Ollama non risponde"
        models = json.loads(r.stdout).get("models", [])
        if not models:
            return "FAILED", "Nessun modello installato"
        return "OK", f"{len(models)} modelli"
    except Exception as e:
        return "FAILED", str(e)


def check_gliner():
    try:
        r = subprocess.run(
            ["curl", "-s", "--max-time", "2", "http://127.0.0.1:8000/health"],
            capture_output=True, text=True, timeout=3
        )
        data = json.loads(r.stdout)
        if data.get("model_loaded"):
            return "OK", data.get("model", "?")
        return "DEGRADED", "GLiNER attivo ma modello non caricato"
    except Exception:
        return "FAILED", "GLiNER non risponde (fallback silenzioso attivo)"


def check_model_in_config():
    try:
        from config import config
        model = config["OLLAMA_MODEL"]
        r = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        if model.split(":")[0] in r.stdout:
            return "OK", model
        return "FAILED", f"{model} NON installato (config punta a modello assente)"
    except Exception as e:
        return "FAILED", str(e)


def check_semantic_hashtags():
    try:
        src = Path("semantic_hashtags.py").read_text()
        if "min_similarity: float = 0.68" in src:
            return "OK", "soglia 0.68"
        return "DEGRADED", "soglia hashtag diversa da 0.68"
    except Exception as e:
        return "FAILED", str(e)


def main():
    checks = {
        "Ollama": check_ollama(),
        "GLiNER": check_gliner(),
        "Modello in config": check_model_in_config(),
        "Soglia hashtag": check_semantic_hashtags(),
    }

    exit_code = 0
    print("╔══════════════════════════════════════╗")
    print("║  iCrawler — Quality Gate pre-volo    ║")
    print("╚══════════════════════════════════════╝")
    for name, (status, detail) in checks.items():
        icon = {"OK": "✅", "DEGRADED": "⚠️", "FAILED": "❌"}[status]
        print(f"  {icon} {name:20s} [{status}] {detail}")
        if status == "FAILED":
            exit_code = 2
        elif status == "DEGRADED" and exit_code == 0:
            exit_code = 1

    if exit_code == 0:
        print("\n🚀 Tutto pronto. Puoi generare.")
    elif exit_code == 1:
        print("\n⚠️  DEGRADED: la pipeline funziona ma con qualità ridotta.")
        print("   Rischio: fallback silenziosi, output scadente.")
    else:
        print("\n❌ FAILED: NON generare. Fixa i problemi sopra.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
