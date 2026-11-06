import ollama
import base64
import json
import re
from PIL import Image, ImageDraw

# 1. Carica l'immagine e convertila in base64
image_path = 'test_pulito.jpg'
with open(image_path, 'rb') as f:
    img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')

# 2. Prompt per Qwen2.5-VL
prompt = """
Guarda il viso in questa immagine. 
Restituisci le coordinate (x, y) espresse in PERCENTUALE (da 0 a 100) per:
- L'occhio sinistro (dal punto di vista di chi guarda)
- L'occhio destro
- Il centro della bocca

Rispondi SOLO con un oggetto JSON valido, senza commenti e senza markdown.
Esempio: {"left_eye": [30, 40], "right_eye": [70, 40], "mouth": [50, 75]}
"""

print("🧠 Chiedo a Qwen2.5-VL di trovare i punti del viso...")

# 3. Chiamata a Ollama
response = ollama.chat(
    model='qwen2.5vl:3b',
    messages=[{
        'role': 'user',
        'content': prompt,
        'images': [img_b64]
    }],
    options={'temperature': 0.0}
)

output_text = response['message']['content']
print("🤖 Risposta del modello:", output_text)

# 4. Estrai il JSON dalla risposta (a prova di errore)
try:
    # Cerca il primo blocco JSON nella stringa
    match = re.search(r'\{.*\}', output_text, re.DOTALL)
    if match:
        coords = json.loads(match.group(0))
    else:
        raise ValueError("Nessun JSON trovato")
        
    print("✅ Coordinate estratte:", coords)

    # 5. Disegna i punti sull'immagine
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Colori: Rosso (Sx), Blu (Dx), Verde (Bocca)
    points = [
        (coords['left_eye'], "red", "Occhio Sx"),
        (coords['right_eye'], "blue", "Occhio Dx"),
        (coords['mouth'], "green", "Bocca")
    ]

    for (x_pct, y_pct), color, label in points:
        px = int((x_pct / 100.0) * w)
        py = int((y_pct / 100.0) * h)
        r = 8 # Raggio del cerchio
        draw.ellipse((px-r, py-r, px+r, py+r), fill=color, outline="white", width=2)
        print(f"📍 {label}: {x_pct}%, {y_pct}% -> Pixel: {px}, {py}")

    # Salva e apri il risultato
    out_path = '/tmp/vlm_landmarks_test.jpg'
    img.save(out_path)
    print(f"💾 Immagine salvata in {out_path}")
    
    import os
    os.system(f"open {out_path}")

except Exception as e:
    print("❌ Errore nell'interpretazione della risposta:", e)
