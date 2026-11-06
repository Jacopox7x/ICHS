"""
iCRAWLER — Validazione automatica dell'output
"""

import re

class OutputValidator:
    def __init__(self, facts):
        self.facts = facts
        self.errors = []
        self.warnings = []
    
    def validate(self, output):
        # 1. Controlla che i fatti siano presenti
        for key, value in self.facts.items():
            if value and value != "DA DEFINIRE" and key != "hashtag":
                if str(value) not in output:
                    self.errors.append(f"Fact '{key}' non trovato nell'output")
        
        # 2. Controlla che non ci siano "DA DEFINIRE" nel core output
        if "DA DEFINIRE" in output and "CREATIVE LAB" in output:
            core = output.split("CREATIVE LAB")[0]
            if "DA DEFINIRE" in core:
                self.warnings.append("Core Output contiene DA DEFINIRE")
        
        # 3. Controlla che le sezioni siano complete
        sections = ["STRATEGIA", "PIANO SOCIAL", "HASHTAG", "CTA", "TIMELINE"]
        for section in sections:
            if section not in output:
                self.warnings.append(f"Sezione '{section}' mancante")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def get_report(self):
        return f"✅ Validazione superata" if not self.errors else f"❌ {len(self.errors)} errori"
