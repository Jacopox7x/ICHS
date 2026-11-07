from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import ollama
import json


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
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File vuoto.")

    visual_desc = extract_visual_description(content)

    # PLACEHOLDER: da collegare a SearXNG + Cognee
    weather = "Roma, 7 Novembre: temperatura attuale 28°C, cielo sereno, caldo anomalo."
    guidelines = "Tono elegante, minimalista. No emoji eccessive."

    verdict = validate_with_art_director(visual_desc, proposed_caption, weather, guidelines)

    return {
        "descrizione_visiva": visual_desc,
        "verdetto": verdict.model_dump(),
    }
