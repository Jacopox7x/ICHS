from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import ollama
import json
import re
import requests
import asyncio
import cognee
from cascading_rag import _search_searxng, get_trending_hashtags
from cognee_manager import get_cognee_context


class ArtDirectorVerdict(BaseModel):
    approvato: bool
    motivazione: str
    suggerimento: str
    stagionale_ok: bool = False
    stagionale_motivo: str = ""
    brand_ok: bool = False
    brand_motivo: str = ""
    storico_ok: bool = False
    storico_motivo: str = ""


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


def get_accademia_context(query: str) -> str:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            cognee.search(
                query_text=query,
                datasets=["accademia_moda"],
                query_type=cognee.SearchType.CHUNKS
            )
        )
        if not results:
            return "Nessun riferimento storico trovato."
        context = "\n\n".join([str(r.get("text", r))[:800] for r in results[:2]])
        return context
    except Exception as e:
        print(f"Errore ricerca Accademia: {e}")
        return "Contesto storico non disponibile."


def get_meteo_reale(citta: str) -> tuple[str, int]:
    """Chiama Open-Meteo per meteo reale. Ritorna (descrizione, temp_min)."""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": citta, "count": 1, "language": "it"},
            timeout=5
        ).json()
        
        if not geo.get("results"):
            return f"Meteo non disponibile per {citta}.", 20
        
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        
        meteo = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_min,temperature_2m_max,weathercode",
                "timezone": "Europe/Rome",
                "forecast_days": 1
            },
            timeout=5
        ).json()
        
        if "daily" not in meteo:
            return f"Meteo non disponibile per {citta}.", 20
        
        t_min = int(meteo["daily"]["temperature_2m_min"][0])
        t_max = int(meteo["daily"]["temperature_2m_max"][0])
        
        if t_min < 5:
            cat = f"INVERNO RIGIDO ({t_min}-{t_max}C): adatto a piumini."
        elif t_min <= 18:
            cat = f"AUTUNNO/FRESCO ({t_min}-{t_max}C): adatto a cappotti di lana."
        elif t_min <= 25:
            cat = f"MITE ({t_min}-{t_max}C): adatto a giacche leggere."
        else:
            cat = f"CALDO ({t_min}-{t_max}C): NON adatto a cappotti pesanti."
        
        return cat, t_min
        
    except Exception as e:
        return f"Errore meteo: {e}", 20




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

    # 2. Brand (Cognee)
    try:
        brand_context = get_cognee_context(proposed_caption, brand_id)
        if not brand_context:
            brand_context = "Linee guida del brand non disponibili in memoria."
    except Exception as e:
        brand_context = f"Errore recupero brand: {str(e)}"

    # 3. Meteo (Open-Meteo - API strutturata, no parsing testo)
    citta = "Cremona" if brand_id == "cosper" else "Milano"
    try:
        weather_context, temp_min = get_meteo_reale(citta)
    except Exception:
        weather_context, temp_min = "Meteo non disponibile.", 20

    # 4. Hashtag (SearXNG)
    try:
        hashtag_context = get_trending_hashtags(proposed_caption)
    except Exception:
        hashtag_context = "Hashtag non disponibili."

    # 5. Accademia (Cognee CHUNKS)
    accademia_context = get_accademia_context(proposed_caption)

    # 6. Rules Engine: usa temp_min da Open-Meteo (gia' numerico)
    # temp_min e' gia' impostato da get_meteo_reale()

    visual_lower = visual_desc.lower()
    is_winter = bool(re.search(r"\b(coat|cappotto|piumino|wool|lana|heavy|pesante|winter)\b", visual_lower))
    is_summer = bool(re.search(r"\b(shorts|pantaloncini|estate|summer|leggero|swimsuit|costume)\b", visual_lower))
    # Se c'e' un capo invernale chiaro, non puo' essere estivo
    if is_winter:
        is_summer = False

    stagionale_ok = True
    stagionale_motivo = f"Temperatura minima: {temp_min}C. Capo: {'invernale' if is_winter else 'estivo' if is_summer else 'neutro'}."

    if is_winter and temp_min > 22:
        stagionale_ok = False
        stagionale_motivo = f"INCOERENZA: Capo invernale a {temp_min}C (troppo caldo)."
    elif is_summer and temp_min < 10:
        stagionale_ok = False
        stagionale_motivo = f"INCOERENZA: Capo estivo a {temp_min}C (troppo freddo)."

    # 7. L'AI scrive SOLO la motivazione
    prompt = f"""Sei un Art Director. Il verdetto e' gia' stato calcolato dal sistema.

VERDETTO: {"OK" if stagionale_ok else "BLOCCATO"}
MOTIVO TECNICO: {stagionale_motivo}
TESTO DEL POST: {proposed_caption}
BRAND: {brand_context}
HASHTAG DI TENDENZA: {hashtag_context}

Istruzioni:
- Se VERDETTO e' BLOCCATO, la motivazione DEVE iniziare con "Il post e' stato bloccato perche': " seguito dal MOTIVO TECNICO. Non parlare di brand, hashtag o altre cose. Cita solo il motivo tecnico.
- Se VERDETTO e' OK, scrivi una motivazione positiva e suggerisci gli hashtag.
- NON menzionare il meteo, le previsioni o le temperature.

Rispondi SOLO con questo JSON:
{{
  "motivazione": "Spiegazione in italiano",
  "suggerimento": "Cosa correggere o hashtag da aggiungere"
}}"""

    try:
        res = ollama.chat(
            model="phi3.5",
            messages=[{"role": "user", "content": prompt}],
            format="json",
            options={"temperature": 0.1}
        )
        data = json.loads(res["message"]["content"])
        motivazione_finale = data.get("motivazione", stagionale_motivo)
        suggerimento_finale = data.get("suggerimento", "")
    except Exception:
        motivazione_finale = stagionale_motivo
        suggerimento_finale = "Nessun suggerimento."

    return {
        "descrizione_visiva": visual_desc,
        "contesto_usato": {
            "meteo": weather_context,
            "brand": brand_context,
            "hashtags": hashtag_context
        },
        "verdetto": {
            "approvato": stagionale_ok,
            "motivazione": motivazione_finale,
            "suggerimento": suggerimento_finale,
            "stagionale_ok": stagionale_ok,
            "stagionale_motivo": stagionale_motivo,
            "brand_ok": True,
            "brand_motivo": "",
            "storico_ok": True,
            "storico_motivo": ""
        }
    }
