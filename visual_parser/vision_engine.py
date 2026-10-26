import json
from visual_parser.schema import OsservazioneL1_L2
from visual_parser.judge import verifica_epistemica

# Questa funzione è un "Mock" (finto). Domani la sostituiremo 
# con la chiamata a Ollama (es. Qwen) o all'API di Unlimited-OCR.
def chiama_modello_vision_mock(percorso_immagine: str) -> str:
    # Simuliamo un modello che restituisce un JSON (a volte può sbagliare)
    finto_output_json = """
    {
      "descrizione_generica": "Un uomo vestito con una giacca scura in uno stadio.",
      "entita": [
        {"tipo": "uomo", "quantita": 1, "posizione": "centro", "certezza": "alta"},
        {"tipo": "stadio", "quantita": 1, "posizione": "sfondo", "certezza": "alta"}
      ],
      "attributi": [
        {"categoria": "colore", "valore": "giacca scura"},
        {"categoria": "materiale", "valore": "erba"}
      ],
      "testo_visibile": "",
      "non_inferences": [
        "Non posso sapere il nome della persona.",
        "Non posso dedurre il punteggio della partita."
      ]
    }
    """
    return finto_output_json

def analizza_immagine(percorso_immagine: str):
    """
    Pipeline completa: Immagine -> Modello -> Parsing JSON -> Validazione -> Judge
    """
    print(f"1. Invio immagine {percorso_immagine} al modello vision...")
    risposta_grezza = chiama_modello_vision_mock(percorso_immagine)
    
    print("2. Estrazione del JSON...")
    try:
        # Pulizia basilare in caso il modello metta i backtick markdown ```json ... ```
        clean_json = risposta_grezza.strip().removeprefix("```json").removesuffix("```").strip()
        dati_dict = json.loads(clean_json)
    except json.JSONDecodeError as e:
        print(f"❌ Errore: il modello non ha restituito un JSON valido. {e}")
        return None
        
    print("3. Validazione dello Schema (Pydantic)...")
    try:
        osservazione = OsservazioneL1_L2(**dati_dict)
    except Exception as e:
        print(f"❌ Errore: il JSON non rispetta lo schema. {e}")
        return None
        
    print("4. Verifica Epistemica (Judge)...")
    valido, errori = verifica_epistemica(osservazione)
    
    if not valido:
        print("🚫 IL JUDGE HA BOCCIATO IL PARSER:")
        for err in errori:
            print(f"   - {err}")
        return None
        
    print("✅ Osservazione approvata. Pronta per il livello L3 (Eidolopoiesis).")
    return osservazione

if __name__ == "__main__":
    # Simuliamo di passare una foto di un rapper allo stadio
    risultato = analizza_immagine("rapper_stadio.jpg")
    
    if risultato:
        print("\n--- OUTPUT STRUTTURATO (L1/L2) ---")
        print(risultato.model_dump_json(indent=2))
