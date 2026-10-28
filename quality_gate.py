import logging
from gliner_client import extract_entities, entities_to_dict

logger = logging.getLogger(__name__)

def validate_entities(brief: str, piano_finale: str) -> dict:
    """
    Estrae le entità dal brief e controlla se il piano finale parla di entità 
    completamente estranee (es. un'altra città).
    """
    print("🛡️  Avvio Quality Gate (Anti-Allucinazione)...")
    
    # 1. Estrai entità dal BRIEF
    try:
        raw_brief = extract_entities(brief)
        entita_brief = entities_to_dict(raw_brief) if raw_brief else {}
    except Exception as e:
        logger.error(f"Errore GLiNER sul brief: {e}")
        return {"valid": False, "error": "Impossibile analizzare il brief"}

    # 2. Controllo specifico per i Luoghi (il problema che abbiamo visto)
    # Se il brief ha un luogo (es. Bologna), il piano non deve parlare di altri luoghi (es. Bergamo)
    luoghi_brief = entita_brief.get("location", [])
    if isinstance(luoghi_brief, str):
        luoghi_brief = [luoghi_brief]
        
    # Lista nera dei luoghi che il modello ha allucinato in passato
    luoghi_vietati = ["Bergamo", "Viareggio", "Milano", "Roma"] 
    
    # Se il brief non menziona un luogo, ma il piano contiene un luogo vietato, è un'allucinazione
    for luogo in luoghi_vietati:
        if luogo.lower() in piano_finale.lower():
            # Ma solo se quel luogo non era nel brief!
            if not any(luogo.lower() in str(lb).lower() for lb in luoghi_brief):
                msg = f"Allucinazione rilevata: il piano parla di {luogo} ma il brief non lo menziona."
                print(f"❌ {msg}")
                return {"valid": False, "error": msg}
                
    print("✅ Quality Gate superato: nessuna allucinazione rilevante.")
    return {"valid": True, "error": None}

if __name__ == "__main__":
    # Test del gate
    brief_test = "Festa di quartiere a Bologna. Target: famiglie."
    
    piano_buono = "Un evento fantastico a Bologna per famiglie e bambini."
    piano_cattivo = "Un evento fantastico a Bergamo per famiglie e bambini."
    
    print("--- TEST 1: Piano Buono ---")
    print(validate_entities(brief_test, piano_buono))
    
    print("\n--- TEST 2: Piano Contaminato ---")
    print(validate_entities(brief_test, piano_cattivo))
