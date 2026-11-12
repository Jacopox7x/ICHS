from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import ollama
import json
import re
import requests
import asyncio
from datetime import datetime
import cognee
from cascading_rag import _search_searxng, get_trending_hashtags
from cognee_manager import get_cognee_context

ESTIVO_KW        = {"costume", "spiaggia", "mare", "swimsuit", "bikini", "shorts", "telo mare"}
INVERNALE_KW     = {"lana", "maglione", "cappotto", "inverno", "piumino", "cashmere"}
COSPER_NO_KW     = {"trekking", "sportivo", "tecnico", "mountain", "montagna",
                    "escursionismo", "alpinismo", "outdoor", "athleisure", "performance"}
IMG_INVERNALE_KW = {"cappotto", "coat", "lana", "maglione", "invern", "sweater", "wool", "piumino"}


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


async def _search_accademia_async(query: str) -> str:
    try:
        results = await cognee.search(
            query_text=query,
            datasets=["accademia_moda"],
            query_type=cognee.SearchType.CHUNKS,
        )
        if not results:
            return ""  # dataset non ancora caricato: silenzioso
        if not results:
            return ""
        context = "\n\n".join([str(r.get("text", r))[:800] for r in results[:2]])
        return context
    except Exception as e:
        print(f"Errore ricerca Accademia: {e}")
        return "Contesto storico non disponibile."


def get_accademia_context(query: str) -> str:
    """Thread-safe: usa thread se dentro event loop (FastAPI)."""
    import threading
    try:
        try:
            asyncio.get_running_loop()
            in_loop = True
        except RuntimeError:
            in_loop = False

        if in_loop:
            result = [""]
            def _runner():
                result[0] = asyncio.run(_search_accademia_async(query))
            t = threading.Thread(target=_runner)
            t.start()
            t.join()
            return result[0]
        else:
            return asyncio.run(_search_accademia_async(query))
    except Exception as e:
        print(f"Errore ricerca Accademia: {e}")
        return "Contesto storico non disponibile."


def get_meteo_reale(citta: str) -> tuple:
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": citta, "count": 1, "language": "it"},
            timeout=5,
        ).json()
        if not geo.get("results"):
            return f"Meteo non disponibile per {citta}.", 20
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        meteo = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": "temperature_2m_min,temperature_2m_max,weathercode",
                "timezone": "Europe/Rome", "forecast_days": 1,
            },
            timeout=5,
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


def _classifica_caption(caption: str) -> str:
    t = (caption or "").lower()
    if any(k in t for k in ESTIVO_KW):
        return "estivo"
    if any(k in t for k in INVERNALE_KW):
        return "invernale"
    return "neutro"


def _valuta_stagione(classe: str, temp_min, mese: int):
    if classe == "estivo":
        if temp_min is not None and temp_min <= 18:
            return False, f"Caption estiva ma T min {temp_min}°C (≤18°C)."
        if mese in (11, 12, 1, 2, 3):
            return False, f"Caption estiva in mese invernale ({mese})."
        return True, "Caption estiva in stagione adeguata."
    if classe == "invernale":
        if temp_min is not None and temp_min <= 22:
            return True, f"Capo invernale con T min {temp_min}°C (≤22°C)."
        return False, f"Capo invernale ma T min {temp_min}°C (>22°C)."
    return True, "Caption neutra, nessuna restrizione stagionale."


def _valuta_brand(caption: str, brand_id: str):
    if (brand_id or "").lower() == "cosper":
        t = (caption or "").lower()
        found = [k for k in COSPER_NO_KW if k in t]
        if found:
            return False, f"Caption con tema {found} non coerente col brand Cosper."
    return True, ""


def _check_coerenza_visiva(classe: str, descrizione_visiva: str):
    if classe == "estivo":
        img = (descrizione_visiva or "").lower()
        if any(k in img for k in IMG_INVERNALE_KW):
            return False, "Incoerenza visiva: caption estiva ma immagine mostra capo invernale."
    return True, ""


def _is_truncated(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if t.endswith("'") or t.endswith("l'"):
        return True
    if not t.endswith((".", "!", "?", "»", ")")):
        return True
    return False


vision_router = APIRouter(prefix="/vision", tags=["vision"])


@vision_router.post("/validate-content")
async def validate_content(
    file: UploadFile = File(...),
    proposed_caption: str = Form(...),
    brand_id: str = Form("cosper"),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File vuoto.")

    visual_desc = extract_visual_description(content)

    try:
        brand_context = get_cognee_context(proposed_caption, brand_id)
        if not brand_context:
            brand_context = "Linee guida del brand non disponibili in memoria."
    except Exception as e:
        brand_context = f"Errore recupero brand: {str(e)}"

    citta = "Cremona" if brand_id == "cosper" else "Milano"
    try:
        weather_context, temp_min = get_meteo_reale(citta)
    except Exception:
        weather_context, temp_min = "Meteo non disponibile.", 20

    try:
        hashtag_context = get_trending_hashtags(proposed_caption)
    except Exception:
        hashtag_context = "Hashtag non disponibili."

    accademia_context = get_accademia_context(proposed_caption)

    mese = datetime.now().month
    classe = _classifica_caption(proposed_caption)
    stagionale_ok, stagionale_motivo = _valuta_stagione(classe, temp_min, mese)
    brand_ok, brand_motivo = _valuta_brand(proposed_caption, brand_id)
    visiva_ok, visiva_motivo = _check_coerenza_visiva(classe, visual_desc)
    approvato = bool(stagionale_ok and brand_ok and visiva_ok)
    motivo_tecnico = "; ".join(filter(None, [stagionale_motivo, brand_motivo, visiva_motivo]))

    prompt = f"""Sei un Art Director. Il verdetto e' gia' stato calcolato dal sistema.

VERDETTO: {"OK" if approvato else "BLOCCATO"}
MOTIVO TECNICO: {motivo_tecnico}
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
  "suggerimento": "Cosa correggere",
  "hashtags_suggeriti": "#tag1, #tag2, #tag3, #tag4, #tag5"
}}"""

    try:
        res = ollama.chat(
            model="phi3.5-fixed",
            messages=[{"role": "user", "content": prompt}],
            format="json",
            options={"temperature": 0.1},
        )
        data = json.loads(res["message"]["content"])
        motivazione_phi = data.get("motivazione", "")
        suggerimento_finale = data.get("suggerimento", "")
        hashtags_suggeriti = data.get("hashtags_suggeriti", "")
        if _is_truncated(motivazione_phi):
            motivazione_finale = motivo_tecnico
        else:
            motivazione_finale = motivazione_phi
        hashtags_nel_sugg = re.findall(r"#\w+", suggerimento_finale)
        if hashtags_nel_sugg and not hashtags_suggeriti:
            hashtags_suggeriti = ", ".join(hashtags_nel_sugg)
            suggerimento_finale = re.sub(r"#\w+", "", suggerimento_finale).strip()
            suggerimento_finale = re.sub(r"[,;]\s*[,;]", ",", suggerimento_finale)
            suggerimento_finale = re.sub(r"[,\s]+$", "", suggerimento_finale)
        if not hashtags_suggeriti:
            hashtags_suggeriti = "#FashionStyle, #OutfitOfTheDay, #BrandAwareness"
    except Exception:
        motivazione_finale = motivo_tecnico
        suggerimento_finale = "Nessun suggerimento."
        hashtags_suggeriti = ""

    return {
        "descrizione_visiva": visual_desc,
        "contesto_usato": {
            "meteo": weather_context,
            "brand": brand_context,
            "hashtags": hashtag_context,
        },
        "verdetto": {
            "approvato": approvato,
            "motivazione": motivazione_finale,
            "suggerimento": suggerimento_finale,
            "stagionale_ok": stagionale_ok,
            "stagionale_motivo": stagionale_motivo,
            "brand_ok": brand_ok,
            "brand_motivo": brand_motivo,
            "visiva_ok": visiva_ok,
            "visiva_motivo": visiva_motivo,
            "storico_ok": True,
            "storico_motivo": "",
            "hashtags_suggeriti": hashtags_suggeriti,
        },
    }
