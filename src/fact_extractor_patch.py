# Aggiungi/modifica questo metodo in fact_extractor.py

def _extract_objective(self, text: str) -> Fact:
    # Pattern migliorati per obiettivi con numeri
    patterns = [
        r'(?:obiettivo|scopo|finalità)\s*[:;]\s*([^.\n]+)',
        r'(?:raccogliere|raggiungere|ottenere)\s+([^.\n]+?)(?:\s+[eE]|\.|$)',
        r'raccogliere\s+([\d.,]+\s*(?:euro|€|mila|milioni)?)',  # Cattura "50.000 euro"
        r'obiettivo\s*[:;]\s*([^.\n]+)',  # Fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Se il valore è solo un numero, aggiungi contesto
            if re.match(r'^[\d.,]+$', value):
                # Cerca il contesto intorno
                context = text[max(0, match.start()-50):match.end()+50]
                if 'euro' in context or '€' in context:
                    value += " euro"
                elif 'mila' in context:
                    value += " mila"
                elif 'milioni' in context:
                    value += " milioni"
            return Fact(value, match.group(0), 0.85, FactStatus.LIKELY, "objective_pattern")
    return Fact(None, None, 0.0, FactStatus.MISSING, "none")
