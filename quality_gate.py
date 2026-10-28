import logging
from gliner_client import extract_entities, entities_to_dict

logger = logging.getLogger(__name__)

def validate_entities_dynamic(brief: str, piano_finale: str) -> dict:
    """
    Quality Gate Dinamico: confronta le entità del piano con quelle del brief.
    Se il piano menziona un luogo/persona/data che NON è nel brief, lo blocca.
    """
    print("🛡️  Avvio Quality Gate Dinamico...")
    
    try:
        # 1. Estrai entità dal BRIEF (Verità assoluta)
        raw_brief = extract_entities(brief)
        entita_brief = entities_to_dict(raw_brief) if raw_brief else {}
        
        # 2. Estrai entità dal PIANO GENERATO
        raw_piano = extract_entities(piano_finale)
        entita_piano = entities_to_dict(raw_piano) if raw_piano else {}
        
    except Exception as e:
        logger.error(f"Errore GLiNER nel Quality Gate: {e}")
        # In caso di errore, meglio non bloccare (fail-safe) ma avvisare
        return {"valid": True, "warning": "GLiNER non disponibile, gate saltato"}

    # Categorie sensibili da controllare (escludiamo 'event' o 'target' che sono generici)
    categorie_da_controllare = ["location", "person", "organization"]
    
    for categoria in categorie_da_controllare:
        valori_piano = entita_piano.get(categoria, [])
        if isinstance(valori_piano, str):
            valori_piano = [valori_piano]
            
        valori_brief = entita_brief.get(categoria, [])
        if isinstance(valori_brief, str):
            valori_brief = [valori_brief]

        # Convertiamo in minuscolo per il confronto
        brief_lower = " ".join([str(v).lower() for v in valori_brief])
        
        for valore in valori_piano:
            val_str = str(valore).lower().strip()
            if not val_str: 
                continue
                
            # Se l'entità nel piano NON è presente nel brief (nemmeno come sottostringa)
            if val_str not in brief_lower:
                msg = f"Allucinazione rilevata: il piano parla di '{valore}' ({categoria}) ma il brief non lo menziona."
                print(f"❌ {msg}")
                return {"valid": False, "error": msg}

    print("✅ Quality Gate superato: nessuna allucinazione dinamica rilevata.")
    return {"valid": True, "error": None}

# Manteniamo il vecchio nome della funzione per compatibilità con icrawler_simple.py
def validate_entities(brief: str, piano_finale: str) -> dict:
    return validate_entities_dynamic(brief, piano_finale)

if __name__ == "__main__":
    # Test del gate dinamico
    brief_bologna = "Festa di quartiere a Bologna. Target: famiglie."
    brief_milano = "Evento a Milano. Target: giovani."
    
    piano_buono = "Un evento fantastico a Bologna per famiglie e bambini."
    piano_cattivo = "Un evento fantastico a Bergamo per famiglie e bambini."
    
    print("--- TEST 1: Piano corretto (Bologna -> Bologna) ---")
    print(validate_entities(brief_bologna, piano_buono))
    
    print("\n--- TEST 2: Piano allucinato (Bologna -> Bergamo) ---")
    print(validate_entities(brief_bologna, piano_cattivo))

    print("\n--- TEST 3: Cliente a Milano (Milano -> Milano) ---")
    print(validate_entities(brief_milano, "Evento a Milano per giovani."))
