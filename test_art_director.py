import ollama
import json

# 1. La descrizione estratta da Moondream (la tua immagine sintetica)
visual_description = """
The image features a square-shaped garment with a dark brown color, possibly a coat or a sweater. 
The garment appears to be made of a fabric with a textured appearance. 
The style of the garment is simple and minimalistic. The lighting is soft and diffused.
"""

# 2. Il testo che l'utente vuole pubblicare
proposed_caption = "Il mio nuovo cappotto autunnale preferito. Pronti per l'inverno? 🧥🍂"

# 3. Contesto meteo volutamente critico (caldo anomalo a novembre)
weather_context = "Roma, 7 Novembre: temperatura attuale 28°C, cielo sereno, caldo anomalo."

# 4. Linee guida brand (finte, per il test)
brand_guidelines = "Tono elegante, minimalista. Non usare emoji eccessive. Focus sulla qualità del tessuto."

# 5. Costruzione del prompt
prompt = f"""Sei un Art Director digitale per un brand fashion. Devi decidere se approvare o bloccare la pubblicazione di un contenuto sui social.

## DESCRIZIONE VISIVA DELL'IMMAGINE
{visual_description}

## TESTO PROPOSTO PER IL POST
{proposed_caption}

## CONTESTO METEO ATTUALE
{weather_context}

## LINEE GUIDA DEL BRAND
{brand_guidelines}

## CRITERI DI VALUTAZIONE
1. Coerenza stagionale: il capo è adatto alla temperatura e al periodo?
2. Coerenza brand: il tono visivo e il testo rispettano le linee guida?
3. Coerenza contestuale: ha senso pubblicare questo contenuto ORA, in questo specifico momento atmosferico/storico?

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza markdown, senza testo aggiuntivo, con questa struttura esatta:
{{"approvato": true/false, "motivazione": "...", "suggerimento": "..."}}"""

print("🧠 Phi 3.5 sta valutando il contenuto...")

try:
    response = ollama.chat(
        model="phi3.5",
        messages=[{"role": "user", "content": prompt}],
        format="json", # Forza l'output in JSON
        options={"temperature": 0.2}
    )
    
    raw_json = response["message"]["content"]
    print("\n=========================================")
    print("📄 RISPOSTA GREZZA DI PHI 3.5:")
    print(raw_json)
    print("=========================================")
    
    # Proviamo a fare il parsing
    data = json.loads(raw_json)
    print("\n✅ PARSING JSON RIUSCITO!")
    print(f"Approvato: {data.get('approvato')}")
    print(f"Motivazione: {data.get('motivazione')}")
    print(f"Suggerimento: {data.get('suggerimento')}")
    
except json.JSONDecodeError:
    print("\n❌ Errore: Phi 3.5 non ha restituito un JSON valido.")
except Exception as e:
    print(f"\n❌ Errore: {e}")
