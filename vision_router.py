from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import ollama
import json
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


def validate_with_art_director(
    visual_description: str,
    proposed_caption: str,
    weather_context: str,
    brand_guidelines: str,
) -> ArtDirectorVerdict:
    prompt = f"""Sei un Art Director digitale per un brand fashion. 
Decidi se approvare la pubblicazione di un contenuto sui social.

## DESCRIZIONE VISIVA
{visual_description}

## TESTO PROPOSTO
{proposed_caption}

## CONTESTO METEO
{weather_context}

## LINEE GUIDA BRAND
{brand_guidelines}

## CRITERI DI VALUTAZIONE (Verificali TUTTI)
1. Coerenza stagionale: il capo è adatto al meteo e al periodo?
2. Coerenza brand: il testo rispetta il tono e le linee guida?
3. Coerenza contestuale: ha senso pubblicare questo contenuto ORA?

Se il contenuto viola anche UNO SOLO di questi criteri, DEVI bloccarlo (approvato: false).
Nella motivazione, indica esplicitamente quale criterio è stato violato.

Rispondi ESCLUSIVAMENTE con un JSON valido con questa struttura:
{{"approvato": true/false, "motivazione": "...", "suggerimento": "..."}}"""

    response = ollama.chat(
        model="phi3.5",
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"temperature": 0.2},
    )
    try:
        data = json.loads(response["message"]["content"])
        return ArtDirectorVerdict(**data)
    except Exception as e:
        return ArtDirectorVerdict(
            approvato=False,
            motivazione=f"Errore di parsing: {e}",
            suggerimento="Revisione manuale richiesta.",
        )


vision_router = APIRouter(prefix="/vision", tags=["vision"])


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
    verdict = validate_with_art_director(visual_desc, proposed_caption, weather_context, brand_context)

    return {
        "descrizione_visiva": visual_desc,
        "contesto_usato": {
            "meteo": weather_context,
            "brand": brand_context
        },
        "verdetto": verdict.model_dump(),
    }

