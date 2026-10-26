"""
gliner_client.py - Client HTTP per il microservizio GLiNER.

Fornisce una funzione per estrarre entita strutturate da un testo
chiamando il microservizio locale su http://127.0.0.1:8000.

Se il servizio non risponde, le funzioni ritornano None e il chiamante
puo fare fallback sul parsing tradizionale.
"""

import json
import urllib.request
import urllib.error

GLINER_URL = "http://127.0.0.1:8000/extract"
GLINER_TIMEOUT = 10  # secondi

# Etichette di default per i brief di content strategy.
# Usiamo etichette in inglese perche GLiNER multi-v2.1 le gestisce meglio
# anche su testo italiano, come verificato nei test.
DEFAULT_LABELS = [
    "event",
    "date",
    "location",
    "target audience",
    "budget",
    "hashtag",
    "organizer",
    "topic",
    "brand",
    "product",
    "person"
]


def extract_entities(text, labels=None, threshold=0.5):
    """
    Chiama il microservizio GLiNER e ritorna una lista di entita.

    Args:
        text: testo da analizzare
        labels: lista di etichette da cercare (default: DEFAULT_LABELS)
        threshold: soglia di confidenza (0-1)

    Returns:
        list di dict con chiavi label, text, start, end, score
        oppure None se il servizio non risponde.
    """
    if labels is None:
        labels = DEFAULT_LABELS

    payload = {
        "text": text,
        "labels": labels,
        "threshold": threshold,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GLINER_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=GLINER_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("entities", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"[gliner_client] servizio non raggiungibile: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[gliner_client] risposta non valida: {e}")
        return None


def entities_to_dict(entities):
    """
    Converte la lista di entita in un dizionario per il PromptBuilder.

    Per ogni label, sceglie l'entita con score piu alto, ma scarta
    le entita che sono identiche o quasi identiche alla loro etichetta
    (probabilmente sono la parola chiave del brief, non il valore).
    """
    if not entities:
        return {}

    by_label = {}
    for e in entities:
        label = e["label"]
        text = e["text"].strip()

        # Scarta se il testo coincide con l'etichetta (case-insensitive)
        label_norm = label.lower().strip()
        text_norm = text.lower().strip().rstrip(":").strip()
        if text_norm == label_norm:
            continue
        # Scarta anche se il testo e un prefisso dell'etichetta
        if label_norm.startswith(text_norm) and len(text_norm) < len(label_norm):
            continue

        if label not in by_label or e["score"] > by_label[label]["score"]:
            by_label[label] = e

    return {label: e["text"] for label, e in by_label.items()}


def is_alive():
    """Verifica rapida che il servizio sia attivo."""
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:8000/health", timeout=2
        ) as resp:
            return resp.status == 200
    except Exception:
        return False
