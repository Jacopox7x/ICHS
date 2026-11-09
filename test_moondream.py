import ollama
import os

IMAGE_PATH = "/Users/jacopogalati/Documents/ICHS/test_fashion.jpg"

if not os.path.exists(IMAGE_PATH):
    print(f"❌ Errore: Il file {IMAGE_PATH} non esiste.")
    exit()

# Verifichiamo che il file non sia vuoto (0 bytes)
file_size = os.path.getsize(IMAGE_PATH)
print(f"📦 Dimensione file: {file_size} bytes")
if file_size == 0:
    print("❌ Errore: Il file è vuoto! Il download con curl è fallito.")
    exit()

# LEGGIAMO L'IMMAGINE COME BYTES
with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

prompt = (
    "Describe this fashion image in extreme detail for an art director. "
    "Focus on: garment type, fabric texture, color palette, styling, "
    "seasonality cues (heavy coat vs light fabric), setting, lighting mood, "
    "and any visible brand elements. Be specific and objective. "
    "Do not invent details that are not visible."
)

print("👁️ Moondream sta guardando l'immagine...")

try:
    # Passiamo image_bytes invece del percorso stringa
    response = ollama.chat(
        model="moondream",
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [image_bytes] 
        }]
    )
    
    print("\n=========================================")
    print("📝 DESCRIZIONE VISIVA ESTRATTA:")
    print("=========================================")
    print(response["message"]["content"])
    print("=========================================\n")
    
except Exception as e:
    print(f"❌ Errore durante l'inferenza: {e}")
