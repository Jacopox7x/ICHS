"""
validator.py - Validatore minimale per i piani social generati.

Questa versione controlla solo che il piano contenga le entita
principali estratte dal brief (evento, data, luogo, target, budget).
Non fa piu i controlli granulari della versione precedente.

Se in futuro serve la validazione completa, si puo espandere questa
classe aggiungendo metodi senza rompere nulla.
"""

from typing import Any, Dict, List


class Validator:

    def __init__(self):
        self.errors: List[str] = []

    def validate(self, output: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica che il piano contenga le entita principali del brief.

        Ritorna un dict con chiavi: valid (bool), errors (list), output (str).
        """
        self.errors = []
        output_lower = output.lower()

        # Verifica entita una per una
        self._check_entity(output_lower, brief, "nome_evento", "nome evento")
        self._check_entity(output_lower, brief, "data", "data")
        self._check_entity(output_lower, brief, "luogo", "luogo")
        self._check_entity(output_lower, brief, "target", "target")
        self._check_entity(output_lower, brief, "budget", "budget")

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "output": output,
        }

    def _check_entity(self, output_lower: str, brief: Dict[str, Any],
                      key: str, label: str) -> None:
        """Controlla che il valore del brief per key sia presente nell'output."""
        value = brief.get(key)
        if not value:
            return
        value = str(value).strip()
        if not value or value.lower().startswith("non specificat"):
            return

        # Estrai parole significative (piu di 3 caratteri) dal valore
        words = [w for w in value.split() if len(w) > 3]
        if not words:
            words = [value]

        # Se almeno una parola e presente nell'output, consideriamo ok
        for w in words:
            if w.lower() in output_lower:
                return

        self.errors.append(f"{label} non trovato nell'output: {value}")
