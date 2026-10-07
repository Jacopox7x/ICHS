"""
iCRAWLER V1.8.1 — API REST
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
from typing import Optional
from pathlib import Path

app = FastAPI(
    title="iCRAWLER API",
    description="Generazione automatica piani social",
    version="1.8.1"
)

class BriefRequest(BaseModel):
    brief: str
    creative_lab: Optional[bool] = True

class PlanResponse(BaseModel):
    success: bool
    plan: str
    creative_lab: Optional[str] = None
    error: Optional[str] = None
    stats: Optional[dict] = None

@app.get("/")
async def root():
    return {
        "service": "iCRAWLER API",
        "version": "1.8.1",
        "status": "operativo",
        "endpoints": [
            "POST /generate",
            "GET /health"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.8.1"}

@app.post("/generate", response_model=PlanResponse)
async def generate_plan(request: BriefRequest):
    """Genera un piano social dal brief"""
    try:
        # Crea file temporaneo per il brief
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(request.brief)
            temp_file = f.name
        
        # Esegui iCRAWLER
        result = subprocess.run(
            [
                "python3",
                str(Path("~/Documents/ICHS/iCRAWLER_KNOWLEDGE_BASE_v1.0/test_interactive_v18_hybrid.py").expanduser()),
                temp_file
            ],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        os.unlink(temp_file)  # Rimuovi file temporaneo
        
        output = result.stdout
        
        # Estrai piano e creative lab
        plan = ""
        creative_lab = ""
        
        if "📋 PIANO COMPLETO" in output:
            try:
                # Estrai il piano dal debug
                lines = output.split('\n')
                in_plan = False
                in_creative = False
                plan_lines = []
                creative_lines = []
                
                for line in lines:
                    if "📋 PIANO COMPLETO" in line:
                        in_plan = True
                        continue
                    if "💡 CREATIVE LAB" in line:
                        in_creative = True
                        in_plan = False
                        continue
                    if "📊 STATISTICHE" in line:
                        in_creative = False
                        continue
                    if in_plan:
                        plan_lines.append(line)
                    elif in_creative:
                        creative_lines.append(line)
                
                plan = "\n".join(plan_lines).strip()
                creative_lab = "\n".join(creative_lines).strip()
                
                # Se il piano è vuoto, usa tutto l'output
                if not plan:
                    plan = output
            except:
                plan = output
                creative_lab = ""
        
        # Estrai statistiche
        stats = {}
        if "Caratteri:" in output:
            for line in output.split('\n'):
                if "Caratteri:" in line:
                    try:
                        stats['caratteri'] = int(line.split(':')[1].strip())
                    except:
                        pass
                if "Reach totale:" in line:
                    try:
                        stats['reach'] = line.split(':')[1].strip()
                    except:
                        pass
        
        return PlanResponse(
            success=True,
            plan=plan,
            creative_lab=creative_lab if request.creative_lab else None,
            stats=stats
        )
        
    except subprocess.TimeoutExpired:
        return PlanResponse(
            success=False,
            plan="",
            creative_lab="",
            error="Timeout: generazione richiesta più di 5 minuti"
        )
    except Exception as e:
        return PlanResponse(
            success=False,
            plan="",
            creative_lab="",
            error=f"Errore: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
