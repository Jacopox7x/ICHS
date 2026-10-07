import json
import re
import subprocess
from typing import Dict, Optional

PROMPT_TEMPLATE = """Estrai i seguenti campi dal brief:

- event_name: il nome dell'evento (NON deve contenere la città)
- date: la data
- location: SOLO il nome della città, senza "a" davanti
- target: il pubblico
- objective: l'obiettivo
- hashtag: se presente

REGOLE FERREE:
1. event_name NON può contenere "a Bologna", "a Milano", "a Roma" o qualsiasi città
2. location è SOLO il nome della città (es. "Bologna", non "a Bologna")
3. Se un campo non è presente, usa "DA DEFINIRE"

Brief: {text}

Rispondi SOLO in JSON valido, senza spiegazioni."""

def parse_response(content: str) -> Dict[str, str]:
    result = {}
    
    json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except:
            pass
    
    patterns = {
        'event_name': r'(?:event_name|nome)[\s:]+["\']?([^"\',\n}]+)',
        'date': r'(?:date|data)[\s:]+["\']?([^"\',\n}]+)',
        'location': r'(?:location|luogo|città)[\s:]+["\']?([^"\',\n}]+)',
        'target': r'(?:target|pubblico)[\s:]+["\']?([^"\',\n}]+)',
        'objective': r'(?:objective|obiettivo)[\s:]+["\']?([^"\',\n}]+)',
        'hashtag': r'(?:hashtag)[\s:]+["\']?([^"\',\n}]+)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            value = match.group(1).strip().strip('",')
            if value and value.lower() not in ['null', 'none']:
                result[key] = value
    
    return result

def extract_with_qwen(text: str) -> Optional[Dict[str, str]]:
    prompt = PROMPT_TEMPLATE.format(text=text)
    
    payload = json.dumps({
        "model": "qwen3.5:4b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.0}
    })
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:11434/api/chat",
             "-H", "Content-Type: application/json", "-d", payload],
            capture_output=True, text=True, timeout=300
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            content = data.get("message", {}).get("content", "")
            parsed = parse_response(content)
            if parsed:
                for field in ['event_name', 'date', 'location', 'target', 'objective', 'hashtag']:
                    if field not in parsed:
                        parsed[field] = 'DA DEFINIRE'
                return parsed
        return None
    except Exception:
        return None
