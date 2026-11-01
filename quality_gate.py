import logging
import re
from gliner_client import extract_entities, entities_to_dict

logger = logging.getLogger(__name__)

def _is_proper_noun(text: str) -> bool:
    """Euristica: è un nome proprio? (es. 'Mario Rossi' sì, 'la nonna' no)."""
    text = text.strip()
    if not text:
        return False
    # Se è composto da parole che iniziano con la maiuscola ed è corto
    words = text.split()
    if len(words) <= 3 and all(w[0].isupper() for w in words if w):
        # Escludiamo parole comuni che GLiNER potrebbe scambiare per nomi
        comuni = ["Nonna", "Nonno", "Bambino", "Bambina", "Famiglia", "DJ", "Artista", "Ospite"]
        if text not in comuni:
            return True
    return False

def validate_entities_dynamic(brief: str, piano_finale: str) -> dict:
    print("🛡️  Avvio Quality Gate Dinamico...")
    try:
        entita_brief = entities_to_dict(extract_entities(brief) or {})
        entita_piano = entities_to_dict(extract_entities(piano_finale) or {})
    except Exception as e:
        logger.error(f"Errore GLiNER nel Quality Gate: {e}")
        return {"valid": True, "warning": "GLiNER non disponibile, gate saltato"}

    # Controlliamo Luoghi e Organizzazioni (sempre severi)
    for categoria in ["location", "organization"]:
        valori_piano = entita_piano.get(categoria, [])
        if isinstance(valori_piano, str): valori_piano = [valori_piano]
        valori_brief = entita_brief.get(categoria, [])
        if isinstance(valori_brief, str): valori_brief = [valori_brief]
        
        brief_lower = " ".join([str(v).lower() for v in valori_brief])
        for valore in valori_piano:
            val_str = str(valore).lower().strip()
            if val_str and val_str not in brief_lower:
                msg = f"Allucinazione: il piano parla di '{valore}' ({categoria}) ma il brief non lo menziona."
                print(f"❌ {msg}")
                return {"valid": False, "error": msg}

    # Controlliamo le Persone (solo se sono nomi propri!)
    valori_persone = entita_piano.get("person", [])
    if isinstance(valori_persone, str): valori_persone = [valori_persone]
    brief_lower = " ".join([str(v).lower() for v in entita_brief.get("person", [])])
    
    # Parole generiche da ignorare (non sono allucinazioni gravi)
    GENERIC_WORDS = ["persona", "persone", "utente", "utenti", "cliente", "clienti", "pubblico"]
    
    for valore in valori_persone:
        val_str = str(valore).strip()
        if val_str.lower() in GENERIC_WORDS:
            continue # Ignora le parole generiche
            
        if _is_proper_noun(val_str) and val_str.lower() not in brief_lower:
            msg = f"Allucinazione: il piano cita la persona '{valore}' ma il brief non la menziona."
            print(f"❌ {msg}")
            return {"valid": False, "error": msg}

    print("✅ Quality Gate superato: nessuna allucinazione critica.")
    return {"valid": True, "error": None}

def validate_entities(brief: str, piano_finale: str) -> dict:
    return validate_entities_dynamic(brief, piano_finale)
