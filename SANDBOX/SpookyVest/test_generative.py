import ollama
import base64
import urllib.parse
import urllib.request
import os

image_path = 'test_pulito.jpg'
print(f"📸 Analizzo l'immagine {image_path}...")

with open(image_path, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')

# --- FASE 1: Qwen-VL descrive l'immagine ---
print("👁️ Qwen2.5-VL sta guardando la foto...")
res_vl = ollama.chat(
    model='qwen2.5vl:3b',
    messages=[{
        'role': 'user',
        'content': "Descrivi questa immagine in modo dettagliato in inglese. Focalizzati sull'aspetto della persona, i vestiti e lo sfondo. Sii sintetico (max 3 frasi).",
        'images': [img_b64]
    }],
    options={'temperature': 0.3}
)
descrizione = res_vl['message']['content'].strip()
print(f"📝 Descrizione: {descrizione}")

# --- FASE 2: Qwen2.5 scrive il prompt Horror ---
print("🧠 Qwen2.5 sta creando il prompt spooky...")
res_llm = ollama.chat(
    model='qwen2.5:3b',
    messages=[{
        'role': 'user',
        'content': f"""Prendi questa descrizione: "{descrizione}"
        Trasformala in un prompt per un generatore di immagini AI.
        L'obiettivo è creare un'immagine spaventosa di Halloween in stile "Funky Semiotics" (fumetto underground, colori forti).
        Sostituisci la faccia della persona con una maschera da zucca di Halloween o un teschio.
        Mantieni i vestiti e lo sfondo originali.
        Rispondi SOLO con il prompt in inglese, senza virgolette e senza commenti."""
    }],
    options={'temperature': 0.7}
)
prompt_finale = res_llm['message']['content'].strip()
print(f"🎃 Prompt Generativo: {prompt_finale}")

# --- FASE 3: Generazione Immagine (Pollinations.ai) ---
print("🪄 Generazione dell'immagine in corso (attendi ~5 secondi)...")
# Aggiungiamo parametri per forzare lo stile fumetto/horror
prompt_encoded = urllib.parse.quote(prompt_finale + ", halloween style, comic book art, highly detailed")
url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true&seed=42"

try:
    out_path = '/tmp/spooky_generated.jpg'
    urllib.request.urlretrieve(url, out_path)
    print(f"✅ Immagine generata e salvata in {out_path}")
    os.system(f"open {out_path}")
except Exception as e:
    print(f"❌ Errore durante il download: {e}")

