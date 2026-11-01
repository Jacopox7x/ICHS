from pathlib import Path
import base64
import tempfile
import os
import io
import sys
import re
import json
import ollama
from PIL import Image

# Apple Vision (solo su macOS)
HAS_APPLE_VISION = False
if sys.platform == "darwin":
    try:
        import Vision
        import Quartz
        from Foundation import NSURL
        HAS_APPLE_VISION = True
    except ImportError:
        pass

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from icrawler_simple import ICrawler
from knowledge_base import get_context_for_brief, get_graph_data, build_and_save_graph
from summarization_agent import SummarizationAgent

from gliner_client import extract_entities, entities_to_dict, is_alive

app = FastAPI(title="iCrawler UI")
app.mount("/static", StaticFiles(directory=Path(__file__).parent), name="static")

crawler = ICrawler()
summarizer = SummarizationAgent()

HTML_FILE = Path(__file__).parent / "ui.html"
HTML_V4 = Path(__file__).parent / "ui_v4.html"
PLANS_DIR = Path(__file__).parent

class BriefRequest(BaseModel):
    brief: str
    mode: str = "social"
    sandbox: str = "cosper"
    usa_contesto: bool = True

class ManualGraphRequest(BaseModel):
    nodes: str
    sandbox: str = "cosper"

class SummarizeRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_FILE.read_text(encoding="utf-8")

@app.get("/v4", response_class=HTMLResponse)
def home_v4():
    if HTML_V4.exists():
        return HTML_V4.read_text(encoding="utf-8")
    return "File ui_v4.html non trovato."

@app.get("/health")
def health():
    return {"status": "ok", "gliner_alive": is_alive()}

@app.post("/extract")
def extract(req: BriefRequest):
    brief = req.brief.strip()
    if not brief:
        return {"entities": {}, "raw": []}
    raw = extract_entities(brief)
    if raw is None:
        return {"entities": {}, "raw": [], "error": "GLiNER non raggiungibile"}
    entities = entities_to_dict(raw)
    return {"entities": entities, "raw": raw}

@app.post("/genera")
def genera(req: BriefRequest):
    brief = req.brief.strip()
    if not brief:
        return {"piano": "Brief vuoto. Incolla un testo prima di generare."}

    if len(brief.split()) < 10:
        return {"piano": "❌ Il brief è troppo corto (meno di 10 parole). Se hai caricato un'immagine, clicca su 'Analisi Visiva' o spunta 'Forza Generazione'."}

    piano = crawler.generate_strategy(brief, mode=req.mode, sandbox=req.sandbox, usa_contesto=req.usa_contesto)
    return {"piano": piano}

@app.post("/summarize")
def summarize_text(req: SummarizeRequest):
    text = req.text.strip()
    if not text or len(text) < 100:
        return {"summary": "Testo troppo corto per essere riassunto."}
    
    try:
        summary = summarizer.summarize(text)
        return {"summary": summary}
    except Exception as e:
        return {"summary": f"Errore: {str(e)}"}

def run_apple_ocr(image_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        temp_img.write(image_bytes)
        temp_path = temp_img.name
    try:
        url = NSURL.fileURLWithPath_(temp_path)
        source = Quartz.CGImageSourceCreateWithURL(url, None)
        image = Quartz.CGImageSourceCreateImageAtIndex(source, 0, None)
        request = Vision.VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLanguages_(["it-IT", "en-US"])
        request.setRecognitionLevel_(0)
        handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, None)
        handler.performRequests_error_([request], None)
        results = request.results()
        if not results:
            return ""
        return "\n".join([obs.topCandidates_(1)[0].string() for obs in results])
    finally:
        os.remove(temp_path)

def run_qwen_ocr(image_bytes: bytes) -> str:
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = """Sei un OCR. Estrai TUTTO il testo visibile in questa immagine. 
Se ci sono date, orari, luoghi o nomi, trascrivili ESATTAMENTE come appaiono. 
Non aggiungere commenti, restituisci solo il testo estratto."""
    response = ollama.chat(
        model="qwen2.5vl:3b",
        messages=[{"role": "user", "content": prompt, "images": [img_b64]}],
        options={"temperature": 0.0, "num_ctx": 8192},
        
    )
    return response["message"]["content"]

MAX_UPLOAD_MB = 8
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}

@app.post("/ocr")
def ocr(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail=f"Tipo non supportato: {file.content_type}")
    try:
        size = 0
        chunks = []
        while chunk := file.file.read(65536):
            size += len(chunk)
            if size > MAX_UPLOAD_MB * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"Immagine troppo grande (max {MAX_UPLOAD_MB} MB)")
            chunks.append(chunk)
        contents = b"".join(chunks)
        
        if HAS_APPLE_VISION:
            testo_estratto = run_apple_ocr(contents)
            print(f"🍎 OCR Apple Vision: '{testo_estratto}'")
        else:
            print("⚠️ Apple Vision non disponibile. Uso Qwen VL per l'OCR...")
            testo_estratto = run_qwen_ocr(contents)
            
        return {"testo": testo_estratto}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e), "testo": ""}

@app.post("/analyze_vision")
def analyze_vision(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        
        # 1. PRIMA PROVIAMO CON APPLE VISION (Istantaneo, zero RAM)
        if HAS_APPLE_VISION:
            print("🍎 Uso Apple Vision per l'OCR...")
            testo_estratto = run_apple_ocr(contents)
            print(f"🍎 OCR Apple Vision: '{testo_estratto}'")
        else:
            testo_estratto = ""

        # 2. SE ABBIAMO IL TESTO, PROVIAMO A DESCRIVERE L'IMMAGINE CON QWEN-VL (Opzionale)
        descrizione = "Descrizione visiva non disponibile."
        try:
            print("👁️ Chiedo a Qwen-VL una descrizione visiva...")
            img_b64 = base64.b64encode(contents).decode("utf-8")
            prompt = "Descrivi questa immagine in modo breve e oggettivo in italiano. Cosa si vede? Rispondi in 1 o 2 frasi."
            
            response = ollama.chat(
                model="qwen2.5vl:3b",
                messages=[{"role": "user", "content": prompt, "images": [img_b64]}],
                options={"temperature": 0.0, "num_ctx": 2048},
                
            )
            descrizione = response["message"]["content"].strip()
        except Exception as e:
            import traceback
            print(f"❌ ERRORE VISION: {e}")
            traceback.print_exc()

        # 3. Restituiamo un formato standard (che la UI si aspetta)
        vision_data = {
            "descrizione_generica": descrizione,
            "testo_visibile": testo_estratto,
            "oggetti": [], 
            "colori": [],
            "non_inferences": []
        }
        
        return {"vision": vision_data}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "vision": None}

@app.get("/storico")
def storico(sandbox: str = "cosper"):
    ws_dir = PLANS_DIR / "workspaces" / sandbox
    ws_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(ws_dir.glob("output_plan_*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    return {
        "plans": [
            {"name": f.name, "size": f.stat().st_size, "mtime": int(f.stat().st_mtime)}
            for f in files[:20]
        ]
    }

@app.get("/storico/{name}")
def leggi_piano(name: str, sandbox: str = "cosper"):
    if "/" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Nome non valido")
    path = PLANS_DIR / "workspaces" / sandbox / name
    if not path.exists() or not path.name.startswith("output_plan_"):
        raise HTTPException(status_code=404, detail="Piano non trovato")
    return {"content": path.read_text(encoding="utf-8")}


@app.get("/api/contesto_cliente")
def api_contesto_cliente(cliente: str = "cosper"):
    try:
        ctx = get_context_for_brief("", cliente)
        return {"status": "ok", "contesto": ctx}
    except Exception as e:
        return {"status": "error", "contesto": str(e)}



@app.post("/api/genera_grafo")
def genera_grafo(req: BriefRequest):
    from graph_manager import build_graph_from_text, get_graph_data
    try:
        # Usiamo solo GLiNER per estrarre le entità
        build_graph_from_text(req.brief, cliente=req.sandbox)
        return get_graph_data()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/grafo_manuale")
def api_grafo_manuale(req: ManualGraphRequest):
    from graph_manager import build_manual_graph
    node_list = [n.strip() for n in req.nodes.split(",") if n.strip()]
    return build_manual_graph(node_list, cliente=req.sandbox)

@app.get("/api/grafo_cliente")
def api_grafo_cliente(cliente: str = "cosper"):

    return get_graph_data()

@app.post("/api/genera_grafo")
def genera_grafo(req: BriefRequest):

    build_and_save_graph(req.brief, req.sandbox)

    return get_graph_data()

@app.get("/api/contesto_cliente")
def api_contesto_cliente(cliente: str = "cosper"):

    # Passiamo un brief fittizio o recuperiamo il contesto generico
    ctx = get_context_for_brief("", cliente)
    return {"status": "ok", "contesto": ctx if ctx else "Nessun contesto trovato."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui_server:app", host="127.0.0.1", port=8080, reload=False)
