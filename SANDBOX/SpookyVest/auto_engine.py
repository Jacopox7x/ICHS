import base64
import ollama
import cv2
import numpy as np
import os
from spooky_engine import SpookyEngine
from generative_engine import GenerativeEngine
from mask_recommender import suggerisci_maschera

class AutoEngine:
    def __init__(self):
        self.veloce = SpookyEngine()
        self.ai = GenerativeEngine()

    async def transform(self, image_bytes: bytes, brief: str = None, quality: str = "auto"):
        log = []
        
        # 1. Rileva volto
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        faces = self.veloce.detector.detect(img) if img is not None else []
        has_face = len(faces) > 0
        log.append(f"Volti rilevati: {len(faces)}")
        
        # 2. Scegli strategia
        strategy = self._choose_strategy(quality, has_face, brief)
        log.append(f"Strategia scelta: {strategy}")
        
        # 3. Auto-genera brief se manca
        if not brief:
            brief = self._auto_generate_brief(image_bytes)
            log.append(f"Brief auto-generato: {brief[:60]}...")
        
        # 4. Esegui con fallback
        try:
            result = self._execute(strategy, image_bytes, brief)
            log.append(f"✅ {strategy} riuscito")
            return result, {"strategy": strategy, "log": log}
        except Exception as e:
            log.append(f"❌ {strategy} fallito: {str(e)}")
            fallback = "ai" if strategy == "fast" else "fast"
            try:
                result = self._execute(fallback, image_bytes, brief)
                log.append(f"✅ Fallback {fallback} riuscito")
                return result, {"strategy": fallback, "log": log, "fallback": True}
            except Exception as e2:
                log.append(f"❌ Anche {fallback} fallito: {str(e2)}")
                return image_bytes, {"strategy": "none", "log": log, "error": str(e2)}

    def _choose_strategy(self, quality, has_face, brief):
        if quality == "fast": return "fast"
        if quality == "ai": return "ai"
        if quality == "max": return "ai"
        if not has_face: return "ai" 
        if brief and any(kw in brief.lower() for kw in ["spaventoso", "horror", "halloween", "zucca", "teschio"]):
            return "ai"
        return "fast" 

    def _auto_generate_brief(self, image_bytes):
        try:
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
            res = ollama.chat(
                model='qwen2.5vl:3b',
                messages=[{
                    'role': 'user',
                    'content': 'Descrivi questa immagine in una frase in italiano. Focalizzati sul soggetto e sull\'atmosfera.',
                    'images': [img_b64]
                }],
                options={'temperature': 0.3}
            )
            return res['message']['content'].strip()
        except:
            return "un ritratto spaventoso"

    def _execute(self, strategy, image_bytes, brief):
        if strategy == "fast":
            recommendation = suggerisci_maschera(brief)
            mask_id = recommendation.get("suggerimento", "pumpkin")
            
            mask_path = f"masks/{mask_id}.png"
            if not os.path.exists(mask_path):
                mask_path = "masks/pumpkin_fix2.png" 
                
            result, error = self.veloce.process_image(image_bytes, mask_path, intensity=0.7)
            if error: raise Exception(error)
            return result
        else:
            result, prompt = self.ai.generate(image_bytes)
            if result is None: raise Exception(prompt)
            return result
