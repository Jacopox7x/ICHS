#!/usr/bin/env python3
"""
iCrawler CLI - Versione minimale per positioning
"""

import sys
from fact_extractor import extract_facts
from positioning import get_positioning_report

def main():
    if len(sys.argv) < 2:
        print("Usage: icrawler <file> [--positioning]")
        sys.exit(1)

    arg = sys.argv[1]
    
    # Se il primo argomento è --help
    if arg in ['-h', '--help']:
        print("Usage: icrawler <file> [--positioning]")
        print("  --positioning : mostra solo il report di posizionamento")
        sys.exit(0)

    # Leggi il file
    try:
        with open(arg, 'r') as f:
            brief_text = f.read()
    except FileNotFoundError:
        print(f"❌ File non trovato: {arg}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore lettura file: {e}")
        sys.exit(1)

    # Se flag --positioning
    if "--positioning" in sys.argv:
        facts = extract_facts(brief_text)
        print(get_positioning_report(brief_text, facts))
        sys.exit(0)

    # Altrimenti, piano completo (da implementare)
    print("⚠️ Piano completo non ancora implementato in questa versione.")
    print("Usa il file originale 'test_interactive_v18_hybrid.py' per il piano completo.")
    sys.exit(1)

if __name__ == "__main__":
    main()
