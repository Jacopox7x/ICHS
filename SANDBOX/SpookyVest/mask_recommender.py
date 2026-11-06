import numpy as np
import ollama
import sys
import os

# Aggiungiamo la root di iCrawler al path per importare gliner_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from gliner_client import extract_entities, entities_to_dict

MASKS_DB = [
    {"id": "meloni", "name": "Giorgia Meloni", "desc": "politica italiana, destra, governo, elezioni, presidente del consiglio", "file": "meloni.png"},
    {"id": "schlein", "name": "Elly Schlein", "desc": "politica italiana, sinistra, opposizione, partito democratico", "file": "schlein.png"},
    {"id": "salvini", "name": "Matteo Salvini", "desc": "politica italiana, lega, immigrazione, sicurezza, Matteo", "file": "salvini.png"}
]

def _get_embedding(text: str):
    r = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return np.array(r["embedding"])

def _cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def suggerisci_maschera(brief_text: str):
    entities = {}
    try:
        raw_entities = extract_entities(brief_text)
        if raw_entities:
            entities = entities_to_dict(raw_entities)
    except Exception as e:
        print(f"GLiNER fallito: {e}")

    # Uniamo brief e entità per la ricerca semantica
    entity_text = " ".join([str(v) for v in entities.values() if v])
    search_query = f"{brief_text} {entity_text}"
    
    try:
        query_vec = _get_embedding(search_query)
    except Exception as e:
        print(f"Ollama non disponibile: {e}")
        return {"suggerimento": "meloni", "nome": "Giorgia Meloni", "confidenza": 0.5}
    
    best_score = -1
    best_mask = MASKS_DB[0]

    for mask in MASKS_DB:
        mask_vec = _get_embedding(mask["desc"])
        score = _cosine_similarity(query_vec, mask_vec)
        print(f"Match {mask['name']}: {score:.3f}")
        if score > best_score:
            best_score = score
            best_mask = mask
            
    if best_score < 0.45:
        return {"suggerimento": None, "motivo": "Nessun personaggio rilevante"}

    return {
        "suggerimento": best_mask["id"], 
        "nome": best_mask["name"],
        "confidenza": round(float(best_score), 2)
    }
