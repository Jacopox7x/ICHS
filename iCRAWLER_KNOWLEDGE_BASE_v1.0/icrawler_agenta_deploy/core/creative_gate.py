"""
CreativeGate V1.8.1
Isola il Creative Lab e previene contaminatione del Core Output.
"""

import re

class CreativeGate:
    """Verifica che le idee creative restino nel Lab e non diventino fatti."""

    LAB_MARKER = "💡 CREATIVE LAB"

    def __init__(self, facts: dict):
        self.facts = {k: str(v).lower() for k, v in facts.items() if v}

    def split(self, plan: str):
        """Divide il piano in (core_output, creative_lab)."""
        idx = plan.find(self.LAB_MARKER)
        if idx == -1:
            return plan, ""
        core = plan[:idx].strip()
        lab = plan[idx:].strip()
        return core, lab

    def scan_contamination(self, core: str) -> list:
        """Trova entità/fatti creativi finiti nel Core Output."""
        flags = []
        core_l = core.lower()
        # Se il Core contiene marker creativi senza il Lab → contaminatione
        creative_terms = ["potremmo immaginare", "suggestivo", "idea creativa:",
                          "concept creativo", "🎨", "💡"]
        for t in creative_terms:
            if t in core_l:
                flags.append(f"Termine creativo '{t}' trovato nel Core Output")
        return flags

    def enforce(self, plan: str) -> tuple[str, list]:
        """Ritorna (piano_pulito, warnings)."""
        core, lab = self.split(plan)
        warnings = self.scan_contamination(core)
        if warnings:
            warn_block = "\n\n⚠️ CREATIVE GATE WARNING:\n" + "\n".join(f"- {w}" for w in warnings)
            core = core + warn_block
        return core + ("\n\n" + lab if lab else ""), warnings

if __name__ == "__main__":
    g = CreativeGate({"event_name": "Tech4Good", "location": "Milano"})
    test = "1. STRATEGIA\nMilano ospita Tech4Good.\n\n💡 CREATIVE LAB\nIdea 1: Titolo: Milano si reinventa"
    out, w = g.enforce(test)
    print(out)
    print("WARNINGS:", w)
