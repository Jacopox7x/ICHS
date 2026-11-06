"""
PromptBuilder V1.8.1
Genera prompt con CREATIVE LAB separato e gerarchia priorità.
"""

class PromptBuilder:
    """Costruisce il prompt strategico onesto + creativo separato."""

    PRIORITY_LEVELS = """
GERARCHIA PRIORITÀ (livelli):
10 FACT              → intoccabili
9  HARD_VALIDATION   → vincoli obbligatori
8  BRIEF_CONSTRAINT  → obbligatori
7  PLATFORM          → vincolanti
6  CONTENT           → guida
5  STYLE             → guida
4-3 BEST_PRACTICE   → suggerisce
2-1 CREATIVE         → propone (SOLO Creative Lab)
"""

    CREATIVE_RULE = """
CREATIVE RULE
Le proposte creative possono introdurre concept, format,
metafore, angolazioni narrative e idee originali non nel brief.
Non possono introdurre nuovi FACTS.
Ogni elemento creativo non verificato deve rimanere nel
Creative Lab e non essere presentato come informazione fattuale.
"""

    def build(self, facts: dict, context: dict) -> str:
        facts_block = self._format_facts(facts)
        kb_block = self._format_kb(context)

        prompt = f"""Sei iCRAWLER, social media strategist facts-based.

{self.PRIORITY_LEVELS}
{self.CREATIVE_RULE}

=== FACTS (dal brief, LIVELLO 10 — intoccabili) ===
{facts_block}

=== KNOWLEDGE BASE (regole operative, LIVELLI 7-9) ===
{kb_block}

=== ISTRUZIONI DI GENERAZIONE ===

FACTUAL INTEGRITY
Non inventare né alterare fatti. Se un dato manca → "DA DEFINIRE".

CREATIVE FREEDOM
Puoi proporre idee originali, concept, format e angolazioni narrative
nel blocco CREATIVE LAB.

BOUNDARY
Le idee creative NON possono diventare fatti.
Le proposte non verificate vanno ESCLUSIVAMENTE nel CREATIVE LAB,
mai nel Core Output.

=== STRUTTURA OUTPUT RICHIESTA ===

1. STRATEGIA
2. PIANO SOCIAL
3. CONTENUTI
4. CTA
5. HASHTAG
6. VISUAL (solo descrittivi da facts)
7. VALIDATION REPORT

────────────────────────
💡 CREATIVE LAB
────────────────────────
Idea 1
Titolo: ...
Concept: ...
Perché funziona: ...
Rischio: ...
Dati necessari: DA DEFINIRE

Idea 2
Titolo: ...
Concept: ...
Perché funziona: ...
Rischio: ...
Dati necessari: DA DEFINIRE
"""
        return prompt

    def _format_facts(self, facts: dict) -> str:
        """Formatta i facts in modo leggibile."""
        lines = []
        for key, value in facts.items():
            if value and value != "DA DEFINIRE":
                lines.append(f"- {key}: {value}")
            else:
                lines.append(f"- {key}: DA DEFINIRE ⚠️")
        return "\n".join(lines)

    def _format_kb(self, context: dict) -> str:
        """Formatta le regole dalla Knowledge Base."""
        if not context:
            return "Nessuna regola specifica trovata."
        
        lines = []
        for rule_type, rules in context.items():
            if rules:
                lines.append(f"\n### {rule_type.upper()}")
                for rule in rules[:5]:  # Limita a 5 per brevità
                    if isinstance(rule, dict):
                        rule_text = rule.get('rule', str(rule))
                        priority = rule.get('priority', 'N/A')
                        lines.append(f"- [P{priority}] {rule_text}")
                    else:
                        lines.append(f"- {rule}")
        return "\n".join(lines) if lines else "Nessuna regola specifica trovata."
