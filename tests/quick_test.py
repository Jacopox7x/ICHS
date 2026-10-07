#!/usr/bin/env python3
"""
Test rapido del Fact Extractor (senza Qwen)
"""

import sys
import time
import os

# Aggiungi src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fact_extractor import FactExtractor, format_facts

# Lista di brief da testare
tests = [
    ("Minimale", "Sagra della Polenta a Cremona\n15 agosto 2026, Cremona"),
    ("Senza nome", "Data: 20 agosto 2026\nLuogo: Milano"),
    ("Lungo", "Serata di beneficenza per l'ospedale pediatrico di Bergamo. 12 dicembre 2026, Teatro Donizetti. Obiettivo: raccogliere 50.000 euro."),
    ("Perfetto", "Tech4Good Summit 2026\nData: 22 agosto 2026\nLuogo: Milano\nTarget: professionisti tech\nObiettivo: promuovere l'innovazione"),
]

extractor = FactExtractor()

print("🕷️ QUICK TEST - Fact Extractor")
print("=" * 60)

for name, brief in tests:
    start = time.time()
    facts = extractor.extract(brief)
    elapsed = time.time() - start
    
    print(f"\n📋 {name} ({elapsed:.3f}s)")
    print("-" * 40)
    print(f"  Evento: {facts['event_name'].value or '❌'}")
    print(f"  Data:   {facts['date'].value or '❌'}")
    print(f"  Luogo:  {facts['location'].value or '❌'}")
    print(f"  Target: {facts['target'].value or '❌'}")
    print(f"  Obiettivo: {facts['objective'].value or '❌'}")
