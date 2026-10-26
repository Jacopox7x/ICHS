"""
gliner_service.py — Microservizio FastAPI per l'estrazione di entità con GLiNER.

Espone un endpoint HTTP che WeKnora (o qualsiasi altro client) può chiamare
durante la pipeline di ingestion per estrarre entità strutturate da un testo.

Avvio:
    uvicorn gliner_service:app --host 127.0.0.1 --port 8000

Test:
    curl -X POST http://127.0.0.1:8000/extract \
      -H "Content-Type: application/json" \
      -d '{"text": "Chiara Pecini lavora all Università di Genova.", "labels": ["persona", "organizzazione"]}'
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from gliner import GLiNER

# ---------------------------------------------------------------- logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("gliner_service")

# ---------------------------------------------------------------- config

MODEL_NAME = "urchade/gliner_multi-v2.1"
DEFAULT_THRESHOLD = 0.5
DEFAULT_LABELS = [
    "persona",
    "organizzazione",
    "luogo",
    "data",
    "progetto",
    "evento",
    "finanziamento",
    "prodotto",
]

# Stato globale del modello. Popolato in startup.
ml: dict[str, Any] = {"model": None}

# ---------------------------------------------------------------- schema

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Testo da analizzare")
    labels: list[str] | None = Field(
        None,
        description="Lista di etichette da cercare. Se omessa, usa quelle di default."
    )
    threshold: float = Field(
        DEFAULT_THRESHOLD,
        ge=0.0, le=1.0,
        description="Soglia minima di confidenza (0-1)"
    )

class Entity(BaseModel):
    label: str
    text: str
    start: int
    end: int
    score: float

class ExtractResponse(BaseModel):
    entities: list[Entity]
    count: int
    model: str

# ---------------------------------------------------------------- lifecycle

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carica il modello all'avvio, lo rilascia alla chiusura."""
    log.info("Caricando modello %s ...", MODEL_NAME)
    ml["model"] = GLiNER.from_pretrained(MODEL_NAME)
    log.info("Modello caricato e pronto.")
    yield
    log.info("Spegnimento: rilascio modello.")
    ml["model"] = None

# ---------------------------------------------------------------- app

app = FastAPI(
    title="GLiNER Extraction Service",
    version="1.0.0",
    description="Microservizio per estrazione entità zero-shot via GLiNER",
    lifespan=lifespan,
)

@app.get("/health")
def health() -> dict[str, Any]:
    """Verifica che il servizio sia vivo e il modello caricato."""
    return {
        "status": "ok",
        "model_loaded": ml["model"] is not None,
        "model": MODEL_NAME,
    }

@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest) -> ExtractResponse:
    """Estrae entità dal testo dato, usando le etichette fornite."""
    model = ml["model"]
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    labels = req.labels if req.labels else DEFAULT_LABELS

    try:
        raw = model.predict_entities(
            req.text,
            labels,
            threshold=req.threshold,
        )
    except Exception as e:
        log.exception("Errore durante predict_entities")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    entities = [
        Entity(
            label=e["label"],
            text=e["text"],
            start=e["start"],
            end=e["end"],
            score=round(float(e["score"]), 4),
        )
        for e in raw
    ]

    log.info("Estratte %d entità da testo di %d caratteri",
             len(entities), len(req.text))

    return ExtractResponse(
        entities=entities,
        count=len(entities),
        model=MODEL_NAME,
    )

# ---------------------------------------------------------------- dev entry

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "gliner_service:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
