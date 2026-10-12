#!/usr/bin/env python3
"""
Test minimo Ordomimesi con llama3.2:3b
"""

from pathlib import Path
import ollama
from datetime import datetime

# --- Configurazione ---
MODEL = "llama3.2:3b"
SYSTEM_PROMPT_PATH = Path("prompts/ordomimesi_sistema.txt")
OUTPUT_DIR = Path("schede")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

def build_user_message(fragments: list[str]) -> str:
    parts = ["Ecco i frammenti da analizzare:\n"]
    for i, frag in enumerate(fragments, 1):
        parts.append(f"--- Frammento {i} ---\n{frag.strip()}\n")
    parts.append("\nProduci ora la scheda ordomimetica seguendo esattamente la struttura richiesta.")
    return "\n".join(parts)

def genera_scheda(fragments: list[str]) -> str:
    system_prompt = load_system_prompt()
    user_message = build_user_message(fragments)

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        options={
            "temperature": 0.3,   # più basso = più fedele alla struttura
            "num_ctx": 4096,      # context ridotto per 8GB
        }
    )
    return response["message"]["content"]

def main():
    # Frammenti di prova (puoi cambiarli)
    fragments = [
        "Il ragno tesse la tela al mattino. Ogni filo è una decisione.",
        "I frammenti digitali si accumulano senza ordine. Serve un metodo per dar loro senso.",
        "Ordomimesi: ordinare ciò che appare disordinato, senza forzare un significato unico.",
        "Un crawler non cerca solo dati. Cerca ricorrenze, tensioni, possibili direzioni."
    ]

    print("Generazione scheda ordomimetica in corso...")
    print(f"Modello: {MODEL}")
    print("-" * 50)

    scheda = genera_scheda(fragments)

    print(scheda)
    print("-" * 50)

    # Salvataggio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"scheda_ordomimesi_{timestamp}.md"
    output_file.write_text(scheda, encoding="utf-8")
    print(f"\nScheda salvata in: {output_file}")

if __name__ == "__main__":
    main()
