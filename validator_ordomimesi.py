#!/usr/bin/env python3
"""
Validator strutturale per schede Ordomimesi.
"""

import re
import sys
import pathlib
from dataclasses import dataclass, field


SEZIONI_ATTESE = [
    "1. Contesto e sorgenti",
    "2. Frammenti chiave",
    "3. Ricorrenze e pattern",
    "4. Tensioni e contrasti",
    "5. Ipotesi interpretative",
    "6. Possibili direzioni di senso",
    "7. Limiti dell'analisi",
    "8. Sintesi operativa",
]

BLACKLIST = [
    "è importante notare",
    "in conclusione",
    "gioca un ruolo fondamentale",
    "gioca un ruolo cruciale",
    "gioca un ruolo chiave",
    "molteplici sfaccettature",
    "complesso e articolato",
]

STORPIATURE = [
    "Ordimimesi", "Ordomimesis", "Ordo mimesi", "Ord o mimesi",
    "Ordo-mimesi", "Ordonimesi", "Ordinimesi", "ordinesi",
    "Ordinemimesi", "ordinemimesi", "ordinemìmesi",
]

VERBI_AZIONE = [
    "raccogli", "confronta", "attendi", "pubblica", "archivia",
    "verifica", "integra", "separa", "mappa", "testa", "campiona",
    "estrai", "collega", "prioritizza",
]


@dataclass
class Esito:
    ok: bool = True
    errori: list = field(default_factory=list)
    warning: list = field(default_factory=list)

    def err(self, msg):
        self.ok = False
        self.errori.append(msg)

    def warn(self, msg):
        self.warning.append(msg)


def valida(scheda: str) -> Esito:
    e = Esito()

    if "Ordomimesi" not in scheda:
        e.warn("Il nome 'Ordomimesi' non compare nella scheda.")
    for storpia in STORPIATURE:
        if storpia.lower() in scheda.lower():
            e.err(f"Storpiatura del nome rilevata: '{storpia}'")

    posizioni = []
    for s in SEZIONI_ATTESE:
        m = re.search(r"^##\s*" + re.escape(s), scheda, re.MULTILINE)
        if not m:
            e.err(f"Sezione mancante: '{s}'")
        else:
            posizioni.append((s, m.start()))
    if len(posizioni) == 8:
        idxs = [p[1] for p in posizioni]
        if idxs != sorted(idxs):
            e.err("Le sezioni non sono nell'ordine atteso.")

    for i, s in enumerate(SEZIONI_ATTESE):
        m = re.search(r"^##\s*" + re.escape(s), scheda, re.MULTILINE)
        if not m:
            continue
        start = m.end()
        if i + 1 < len(SEZIONI_ATTESE):
            m2 = re.search(r"^##\s*" + re.escape(SEZIONI_ATTESE[i+1]), scheda, re.MULTILINE)
            end = m2.start() if m2 else len(scheda)
        else:
            end = len(scheda)
        corpo = scheda[start:end].strip()
        if len(corpo) < 30:
            e.err(f"Sezione '{s}' troppo corta ({len(corpo)} caratteri).")

    basso = scheda.lower()
    for b in BLACKLIST:
        if b in basso:
            e.warn(f"Formula generica rilevata: '{b}'")

    m5 = re.search(r"^##\s*5\..*?(?=^##\s*6\.|\Z)", scheda, re.MULTILINE | re.DOTALL)
    if m5:
        blocco = m5.group(0)
        ipotesi = re.findall(r"Ipotesi:.*?(?=Ipotesi:|\Z)", blocco, re.DOTALL)
        if not ipotesi:
            e.warn("Nessuna riga 'Ipotesi:' trovata in sezione 5.")
        for ip in ipotesi:
            if not re.search(r"\(si basa su:.*?\)", ip, re.IGNORECASE):
                e.warn(f"Ipotesi senza riferimento a frammenti: '{ip.strip()[:60]}...'")

    m8 = re.search(r"^##\s*8\..*$", scheda, re.MULTILINE | re.DOTALL)
    if m8:
        corpo8 = m8.group(0).lower()
        if not any(v in corpo8 for v in VERBI_AZIONE):
            e.warn("Sezione 8 sembra priva di verbi d'azione concreti.")

    return e


def stampa(esito: Esito):
    if esito.ok and not esito.warning:
        print("OK — nessun problema rilevato.")
        return
    if esito.ok:
        print("OK con warning:")
    else:
        print("FALLITO:")
    for err in esito.errori:
        print(f"   X {err}")
    for w in esito.warning:
        print(f"   ! {w}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 validator_ordomimesi.py <file_scheda.md>")
        sys.exit(1)
    testo = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    esito = valida(testo)
    stampa(esito)
    sys.exit(0 if esito.ok else 1)
