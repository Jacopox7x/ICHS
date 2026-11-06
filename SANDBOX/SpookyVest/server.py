from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import json
from auto_engine import AutoEngine

app = FastAPI(title="SpookyVest Sandbox")
auto_engine = AutoEngine()

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/transform")
async def transform(
    file: UploadFile = File(...),
    brief: str = Form(None),
    quality: str = Form("auto")
):
    try:
        image_bytes = await file.read()
        result, metadata = await auto_engine.transform(image_bytes, brief, quality)
        
        # Stampa i log nel terminale per vedere cosa ha deciso il cervello
        print("\n".join(metadata["log"]))
        
        return Response(
            content=result,
            media_type="image/jpeg",
            headers={"X-Spooky-Metadata": json.dumps(metadata)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🎃 Avvio SpookyVest Sandbox (Zero-Command Mode) su http://localhost:8081")
    uvicorn.run(app, host="127.0.0.1", port=8081)
