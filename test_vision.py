import ollama
import base64
import sys

print("Incolla il percorso dell'immagine (es. ~/Desktop/locandina.jpg):")
path = input("> ").strip().replace("'", "").replace('"', '').replace("~", "/Users/jacopogalati")

try:
    with open(path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
except FileNotFoundError:
    print("❌ File non trovato. Riprova.")
    sys.exit(1)

print("⏳ Caricamento modello Vision in RAM e analisi dell'immagine (attendi 15-30 secondi)...")

prompt = """Sei un OCR. Estrai TUTTO il testo visibile in questa immagine, mantenendo la formattazione originale il più possibile. 
Se ci sono date, orari, luoghi o nomi, assicurati di trascriverli ESATTAMENTE come appaiono. 
Non aggiungere commenti o introduzioni, restituisci solo il testo estratto."""

response = ollama.chat(
    model="qwen2.5vl:3b",
    messages=[{"role": "user", "content": prompt, "images": [img_b64]}],
    options={"temperature": 0.0},
    keep_alive=0  # FONDAMENTALE: Scarica il modello dalla RAM appena finisce
)

print("\n--- TESTO ESTRATTO ---")
print(response["message"]["content"])
print("----------------------")
print("✅ Modello scaricato dalla RAM (keep_alive=0).")
