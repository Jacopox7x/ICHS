from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import ollama
import json
import cognee
import asyncio
from cascading_rag import _search_searxng
from cognee_manager import get_cognee_context


class ArtDirectorVerdict(BaseModel):
    approvato: bool
    motivazione: str
    suggerimento: str


def extract_visual_description(image_bytes: bytes) -> str:
    prompt = (
        "Describe this fashion image in extreme detail for an art director. "
        "Focus on: garment type, fabric texture, color palette, styling, "
        "seasonality cues (heavy coat vs light fabric), setting, lighting mood. "
        "Be specific and objective. Do not invent details."
    )
    response = ollama.chat(
        model="moondream",
        messages=[{"role": "user", "content": prompt, "images": [image_bytes]}],
    )
    return response["message"]["content"]


    prompt = f"""Sei un Art Director digitale spietato e rigoroso. Devi valutare un post per un brand fashion.

## DATI IN INGRESSO
- Descrizione Visiva: {visual_description}
- Testo Proposto: {proposed_caption}
- Meteo: {weather_context}
- Linee Guida Brand: {brand_guidelines}
- Conoscenza Storica (Accademia): {accademia_context}

## ISTRUZIONI
Valuta il post secondo questi 4 criteri. Se UNO SOLO fallisce, il post è BLOCCATO.
Devi menzionare esplicitamente quale criterio ha fallito nella motivazione.

1. COERENZA STAGIONALE: Il capo visivo è adatto al meteo indicato?
2. COERENZA BRAND: Il testo rispetta il tono e le linee guida?
3. COERENZA CONTESTUALE: Ha senso pubblicare questo ORA?
4. ACCURATEZZA STORICA: Il testo contiene errori storici? (Usa la Conoscenza Storica per verificare. Es. Se dice che Poiret è degli anni '50, è un errore).

Rispondi ESCLUSIVAMENTE con un JSON valido con questa struttura:
{{"approvato": true/false, "motivazione": "...", "suggerimento": "..."}}"""

    response = ollama.chat(
        model="phi3.5",
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"temperature": 0.2},
    )


vision_router = APIRouter(prefix="/vision", tags=["vision"])



def get_accademia_context(query: str) -> str:
    """Cerca nel database dell'Accademia i testi più rilevanti."""
    try:
        # Eseguiamo la ricerca asincrona in modo sincrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            cognee.search(
                query_text=query,
                datasets=["test_storia_moda"],
                query_type=cognee.SearchType.CHUNKS
            )
        )
        
        if not results:
            return "Nessun riferimento storico trovato."
        
        # Prendiamo i primi 3 chunk e uniamoli
        context = "

".join([str(res.get('text', res))[:800] for res in results[:3]])
        return context
        
    except Exception as e:
        print(f"⚠️ Errore ricerca Accademia: {e}")
        return "Contesto storico non disponibile."

# --- INIZIO PATCH ENDPOINT ---

@vision_router.post("/validate-content")
async def validate_content(
    file: UploadFile = File(...),
    proposed_caption: str = Form(...),
    brand_id: str = Form("cosper")
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File vuoto.")

    # 1. Vision
    visual_desc = extract_visual_description(content)

    # 2. Contesto Brand (Cognee)
    try:
        brand_context = get_cognee_context(proposed_caption, brand_id)
        if not brand_context:
            brand_context = "Linee guida del brand non disponibili in memoria."
    except Exception as e:
        brand_context = f"Errore recupero brand: {str(e)}"

    # 3. Contesto Meteo (SearXNG)
    # Cerchiamo il meteo. Se il brand è cosper (Cremona), cerchiamo lì.
    citta = "Cremona" if brand_id == "cosper" else "Milano" 
    try:
        weather_search = _search_searxng(f"meteo {citta} oggi")
        weather_context = weather_search if weather_search else "Meteo non disponibile."
    except Exception:
        weather_context = "Meteo non disponibile."

    # 4. Reasoning
    
    # 3. Recupero Contesto Accademia
    accademia_context = get_accademia_context(proposed_caption)
    
    # 4. Reasoning (con il nuovo contesto)
    verdict = validate_with_art_director(visual_desc, proposed_caption, weather_context, brand_context, accademia_context)


    return {
        "descrizione_visiva": visual_desc,
        "contesto_usato": {
            "meteo": weather_context,
            "brand": brand_context
        },
        "verdetto": verdict.model_dump(),
    }

