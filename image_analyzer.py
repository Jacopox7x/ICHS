"""
Analisi di immagini per iCrawler.
Estrae testo, colori, mood e genera brief.
"""

import re
from PIL import Image
import pytesseract
from colorthief import ColorThief

class ImageAnalyzer:
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff']
    
    def extract_text(self, image_path: str) -> str:
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='ita+eng')
            text = re.sub(r'\n+', '\n', text).strip()
            return text
        except Exception as e:
            print(f"⚠️ Errore OCR: {e}")
            return ""
    
    def extract_colors(self, image_path: str) -> dict:
        try:
            color_thief = ColorThief(image_path)
            palette = color_thief.get_palette(color_count=5)
            
            color_names = {
                (255,0,0): "Rosso", (0,255,0): "Verde", (0,0,255): "Blu",
                (255,255,0): "Giallo", (255,165,0): "Arancione", (128,0,128): "Viola",
                (255,192,203): "Rosa", (0,0,0): "Nero", (255,255,255): "Bianco",
                (128,128,128): "Grigio", (139,69,19): "Marrone", (0,128,128): "Teal"
            }
            
            def closest_color(rgb):
                r, g, b = rgb
                min_dist = float('inf')
                closest = "Sconosciuto"
                for (cr, cg, cb), name in color_names.items():
                    dist = (r-cr)**2 + (g-cg)**2 + (b-cb)**2
                    if dist < min_dist:
                        min_dist = dist
                        closest = name
                return closest
            
            return {
                "rgb": palette,
                "names": [closest_color(c) for c in palette],
                "hex": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]
            }
        except Exception as e:
            print(f"⚠️ Errore colori: {e}")
            return {"rgb": [], "names": [], "hex": []}
    
    def detect_mood(self, colors: list) -> str:
        if not colors:
            return "neutro"
        warm = sum(1 for r, g, b in colors if r > g and r > b)
        cool = sum(1 for r, g, b in colors if b > r and b > g)
        bright = sum(1 for r, g, b in colors if r + g + b > 400)
        dark = len(colors) - bright
        
        if warm > cool and bright > dark:
            return "energico, caldo, vivace"
        elif warm > cool and dark > bright:
            return "intenso, drammatico, caldo"
        elif cool > warm and bright > dark:
            return "fresco, moderno, luminoso"
        elif cool > warm and dark > bright:
            return "elegante, sofisticato, notturno"
        else:
            return "equilibrato, naturale, armonioso"
    
    def generate_brief(self, image_path: str) -> dict:
        print(f"🖼️ Analizzo immagine: {image_path}")
        text = self.extract_text(image_path)
        colors = self.extract_colors(image_path)
        mood = self.detect_mood(colors['rgb'])
        
        brief_lines = []
        event_name = self._extract_event_name(text)
        date = self._extract_date(text)
        location = self._extract_location(text)
        
        if event_name:
            brief_lines.append(f"Evento: {event_name}")
        if date:
            brief_lines.append(f"Data: {date}")
        if location:
            brief_lines.append(f"Luogo: {location}")
        
        brief_lines.append(f"Descrizione: Immagine con mood {mood}. Colori: {', '.join(colors['names'])}.")
        if text:
            brief_lines.append(f"Testo rilevato: {text[:200]}...")
        
        return {
            "brief": "\n".join(brief_lines),
            "text": text,
            "colors": colors,
            "mood": mood,
            "event_name": event_name,
            "date": date,
            "location": location
        }
    
    def _extract_event_name(self, text: str) -> str:
        patterns = [
            r'(?i)evento[:\s]+([^\n]+)',
            r'(?i)([A-Z][a-z]+ [A-Z][a-z]+ \d{4})',
            r'(?i)([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_date(self, text: str) -> str:
        patterns = [
            r'(\d{1,2}\s+[a-zA-Z]+\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{1,2}-\d{1,2})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_location(self, text: str) -> str:
        patterns = [
            r'(?i)luogo[:\s]+([^\n]+)',
            r'(?i)([A-Z][a-z]+,\s+[A-Z][a-z]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

if __name__ == "__main__":
    print("✅ image_analyzer.py caricato correttamente")
