"""
test_rules_only.py — Testa SOLO le regole deterministiche del vision_router.
Niente immagini, nente Moondream, nente API: chiama direttamente le funzioni
_classifica_caption / _valuta_stagione / _valuta_brand / _check_coerenza_visiva.

Così verifichiamo la logica pura, indipendente dal modello vision.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vision_router import (
    _classifica_caption,
    _valuta_stagione,
    _valuta_brand,
    _check_coerenza_visiva,
)


# 5 casi di test con:
# - caption (proposed_caption)
# - brand_id
# - temp_min (simulato)
# - mese (simulato)
# - descrizione_visiva (simulata — serve solo per _check_coerenza_visiva)
# - expected_approvato
CASES = [
    {
        "id": 1,
        "caption": "Pronti per la spiaggia con il costume estivo!",
        "brand_id": "cosper",
        "temp_min": 10, "mese": 11,
        "descrizione_visiva": "A heavy brown wool coat with long sleeves.",
        "expected": False,
    },
    {
        "id": 2,
        "caption": "Elegante completo in lana per l'inverno.",
        "brand_id": "cosper",
        "temp_min": 10, "mese": 11,
        "descrizione_visiva": "A grey wool suit with classic tailoring.",
        "expected": True,
    },
    {
        "id": 3,
        "caption": "Scarpe da trekking per la montagna.",
        "brand_id": "cosper",
        "temp_min": 5, "mese": 12,
        "descrizione_visiva": "Brown hiking boots with thick soles and laces.",
        "expected": False,
    },
    {
        "id": 4,
        "caption": "Maglione di lana per le serate fresche.",
        "brand_id": "cosper",
        "temp_min": 15, "mese": 10,
        "descrizione_visiva": "A dark blue wool sweater with ribbed cuffs.",
        "expected": True,
    },
    {
        "id": 5,
        "caption": "Costume da bagno a pois per Natale.",
        "brand_id": "cosper",
        "temp_min": 5, "mese": 12,
        "descrizione_visiva": "A polka-dot swimsuit on a hanger.",
        "expected": False,
    },
]


def evaluate_case(c: dict) -> dict:
    classe = _classifica_caption(c["caption"])
    stag_ok, stag_motivo = _valuta_stagione(classe, c["temp_min"], c["mese"])
    brand_ok, brand_motivo = _valuta_brand(c["caption"], c["brand_id"])
    vis_ok, vis_motivo = _check_coerenza_visiva(classe, c["descrizione_visiva"])
    approvato = bool(stag_ok and brand_ok and vis_ok)
    return {
        "id": c["id"],
        "classe": classe,
        "stagionale_ok": stag_ok, "stagionale_motivo": stag_motivo,
        "brand_ok": brand_ok, "brand_motivo": brand_motivo,
        "visiva_ok": vis_ok, "visiva_motivo": vis_motivo,
        "approvato": approvato,
        "expected": c["expected"],
        "correct": approvato == c["expected"],
    }


def main():
    print("🧪 TEST RULES-ONLY (logica pura, niente Moondream)\n")
    print("=" * 78)
    print(f"{'ID':>3} {'Classe':<10} {'Stag':<5} {'Brand':<6} {'Vis':<5} {'Appr':<6} {'Exp':<5} {'OK':<4}")
    print("=" * 78)

    results = []
    correct_count = 0
    for c in CASES:
        r = evaluate_case(c)
        results.append(r)
        if r["correct"]:
            correct_count += 1
        print(f"{r['id']:>3} {r['classe']:<10} "
              f"{'✓' if r['stagionale_ok'] else '✗':<5} "
              f"{'✓' if r['brand_ok'] else '✗':<6} "
              f"{'✓' if r['visiva_ok'] else '✗':<5} "
              f"{str(r['approvato']):<6} "
              f"{str(r['expected']):<5} "
              f"{'✅' if r['correct'] else '❌':<4}")

    print("=" * 78)
    print(f"\nAccuracy: {correct_count}/{len(CASES)} = {correct_count/len(CASES)*100:.0f}%\n")

    # Dettaglio per ogni caso
    print("─" * 78)
    print("DETTAGLIO:")
    print("─" * 78)
    for r in results:
        marker = "✅" if r["correct"] else "❌"
        print(f"\n{marker} CASO {r['id']}: classe={r['classe']}")
        print(f"   Stagionale: {'OK' if r['stagionale_ok'] else 'BLOCCATO'} — {r['stagionale_motivo']}")
        if r["brand_motivo"]:
            print(f"   Brand:      {'OK' if r['brand_ok'] else 'BLOCCATO'} — {r['brand_motivo']}")
        else:
            print(f"   Brand:      OK — nessuna violazione Cosper")
        if r["visiva_motivo"]:
            print(f"   Visiva:     {'OK' if r['visiva_ok'] else 'BLOCCATO'} — {r['visiva_motivo']}")
        else:
            print(f"   Visiva:     OK — coerenza caption/immagine")
        print(f"   → approvato={r['approvato']} | expected={r['expected']}")


if __name__ == "__main__":
    main()
