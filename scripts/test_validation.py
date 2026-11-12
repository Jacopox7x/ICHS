import csv
import time
import requests
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

API_URL = "http://127.0.0.1:8080/vision/validate-content"
IMG_DIR = Path(__file__).resolve().parent.parent / "validation" / "images"
OUT_CSV = Path(__file__).resolve().parent.parent / "validation" / "results.csv"

CASES = [
    {"img": "caso_001.jpg", "caption": "Pronti per la spiaggia con il costume estivo!",
     "brand_id": "cosper", "expected": False},
    {"img": "caso_002.jpg", "caption": "Elegante completo in lana per l'inverno.",
     "brand_id": "cosper", "expected": True},
    {"img": "caso_003.jpg", "caption": "Scarpe da trekking per la montagna.",
     "brand_id": "cosper", "expected": False},
    {"img": "caso_004.jpg", "caption": "Maglione di lana per le serate fresche.",
     "brand_id": "cosper", "expected": True},
    {"img": "caso_005.jpg", "caption": "Costume da bagno a pois per Natale.",
     "brand_id": "cosper", "expected": False},
]


def call_api(image_path: Path, caption: str, brand_id: str) -> dict:
    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f, "image/jpeg")}
        data = {"proposed_caption": caption, "brand_id": brand_id}
        r = requests.post(API_URL, files=files, data=data, timeout=60)
    r.raise_for_status()
    return r.json()


def extract_verdict(api_data: dict) -> tuple:
    if not isinstance(api_data, dict):
        return None, ""
    verdetto = api_data.get("verdetto")
    if isinstance(verdetto, dict) and "approvato" in verdetto:
        return verdetto.get("approvato"), verdetto.get("motivazione", "")
    return api_data.get("approvato"), api_data.get("motivazione", "")


def main():
    print("🚀 Inizio validazione su 5 casi...\n")
    rows = []
    y_true, y_pred = [], []

    for i, case in enumerate(CASES, 1):
        img_path = IMG_DIR / case["img"]
        if not img_path.exists():
            print(f"➡️  Test {i}: IMMAGINE MANCANTE {case['img']}, salto.")
            continue
        caption_short = case["caption"][:35] + "..." if len(case["caption"]) > 35 else case["caption"]
        print(f"➡️  Test {i}: {caption_short}")
        t0 = time.time()
        try:
            api_data = call_api(img_path, case["caption"], case["brand_id"])
            pred, motivo = extract_verdict(api_data)
            elapsed = time.time() - t0
            status = "✅" if pred == case["expected"] else "❌"
            print(f"   {status} Atteso: {case['expected']} | Predetto: {pred} ({elapsed:.1f}s)")
            rows.append({
                "id": i, "expected": case["expected"],
                "predicted": pred if pred is not None else "",
                "correct": pred == case["expected"],
                "time_sec": round(elapsed, 2),
                "motivazione_api": (motivo or "")[:200],
            })
            y_true.append(case["expected"])
            y_pred.append(pred)
        except Exception as e:
            elapsed = time.time() - t0
            print(f"   ❌ Errore API: {e} ({elapsed:.1f}s)")
            rows.append({
                "id": i, "expected": case["expected"], "predicted": "ERROR",
                "correct": False, "time_sec": round(elapsed, 2),
                "motivazione_api": str(e)[:200],
            })
            y_true.append(case["expected"])
            y_pred.append(None)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "expected", "predicted", "correct", "time_sec", "motivazione_api"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✅ Risultati salvati in {OUT_CSV}")

    print("\n" + "=" * 40)
    print("📊 METRICHE DI VALUTAZIONE")
    print("=" * 40)
    valid = [(t, bool(p)) for t, p in zip(y_true, y_pred) if p is not None and p != "ERROR"]
    y_true_f = [t for t, _ in valid]
    y_pred_f = [p for _, p in valid]
    if not y_true_f:
        print("Nessuna predizione valida per le metriche.")
    else:
        print(f"Accuracy:  {accuracy_score(y_true_f, y_pred_f) * 100:.2f}%")
        print(f"Precision: {precision_score(y_true_f, y_pred_f, zero_division=0):.2f}")
        print(f"Recall:    {recall_score(y_true_f, y_pred_f, zero_division=0):.2f}")
        print(f"F1-Score:  {f1_score(y_true_f, y_pred_f, zero_division=0):.2f}")
    print("=" * 40)
    avg_time = sum(r["time_sec"] for r in rows) / max(len(rows), 1)
    print(f"⏱️  Tempo medio per validazione: {avg_time:.1f} secondi")


if __name__ == "__main__":
    main()
