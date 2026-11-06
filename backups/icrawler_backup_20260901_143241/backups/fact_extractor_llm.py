"""
Fact Extractor con Qwen - SENZA loop circolari
"""

import json
import re
import requests
from typing import Dict

def extract_facts_with_qwen(text: str) -> Dict[str, str]:
    """Estrae facts usando Qwen"""
    
    prompt = f"""Sei un estrattore di dati. Ricevi un brief di un evento e restituisci i campi richiesti in JSON.

**IMPORTANTE:**
- event_name: il nome dell'evento (NON contiene mai data o città)
- date: la data (es. "10 Settembre", "20-22 agosto")
- location: la città (es. "Rovigo", "Bologna") - NON il tema dell'evento
- target: il pubblico (es. "operai e manager")
- objective: l'obiettivo (es. "promuovere la cultura della birra")
- hashtag: hashtag menzionati (es. "#StartupTorino")

**ESEMPI:**
Input: "Fiera del mattone il 10 Settembre a Rovigo. Per operai e manager."
Output: {{"event_name": "Fiera del mattone", "date": "10 Settembre", "location": "Rovigo", "target": "operai e manager", "objective": "DA DEFINIRE", "hashtag": "DA DEFINIRE"}}

Input: "Festival della Birra Artigianale, 20-22 agosto a Bologna. Per appassionati. Promuovere la cultura della birra."
Output: {{"event_name": "Festival della Birra Artigianale", "date": "20-22 agosto", "location": "Bologna", "target": "appassionati", "objective": "Promuovere la cultura della birra", "hashtag": "DA DEFINIRE"}}

Input: "Startup Meetup 2026 il 3 dicembre a Torino. Per founder e investitori. Networking. #StartupTorino"
Output: {{"event_name": "Startup Meetup 2026", "date": "3 dicembre", "location": "Torino", "target": "founder e investitori", "objective": "Networking", "hashtag": "#StartupTorino"}}

Brief: {text}

Rispondi SOLO con JSON.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen:7b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.0}
            },
            timeout=45
        )
        
        if response.status_code == 200:
            content = response.json()["message"]["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                facts = json.loads(json_match.group(0))
                return {
                    'event_name': facts.get('event_name', 'DA DEFINIRE'),
                    'date': facts.get('date', 'DA DEFINIRE'),
                    'location': facts.get('location', 'DA DEFINIRE'),
                    'organizer': facts.get('organizer', 'DA DEFINIRE'),
                    'target': facts.get('target', 'DA DEFINIRE'),
                    'objective': facts.get('objective', 'DA DEFINIRE'),
                    'time': 'DA DEFINIRE',
                    'venue': 'DA DEFINIRE',
                    'speaker': 'DA DEFINIRE',
                    'budget': 'DA DEFINIRE',
                    'link': 'DA DEFINIRE',
                    'hashtag': facts.get('hashtag', 'DA DEFINIRE')
                }
        
        # Se Qwen fallisce, usa un fallback MINIMALE (senza import circolari)
        print("⚠️ Qwen fallita, uso fallback minimale")
        return extract_facts_fallback(text)
        
    except Exception as e:
        print(f"⚠️ Errore Qwen: {e}, uso fallback minimale")
        return extract_facts_fallback(text)


def extract_facts_fallback(text: str) -> Dict[str, str]:
    """Fallback minimale - senza dipendenze circolari"""
    facts = {
        'event_name': 'DA DEFINIRE',
        'date': 'DA DEFINIRE',
        'location': 'DA DEFINIRE',
        'organizer': 'DA DEFINIRE',
        'target': 'DA DEFINIRE',
        'objective': 'DA DEFINIRE',
        'time': 'DA DEFINIRE',
        'venue': 'DA DEFINIRE',
        'speaker': 'DA DEFINIRE',
        'budget': 'DA DEFINIRE',
        'link': 'DA DEFINIRE',
        'hashtag': 'DA DEFINIRE'
    }
    
    # Regex semplici per salvare il salvabile
    date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+)', text)
    if date_match:
        facts['date'] = date_match.group(1)
    
    city_match = re.search(r'a\s+([A-Z][a-z]+)', text)
    if city_match:
        facts['location'] = city_match.group(1)
    
    target_match = re.search(r'(?:per|rivolto a)\s+([^.,;]+)', text, re.IGNORECASE)
    if target_match:
        facts['target'] = target_match.group(1).strip()
    
    # Se tutto fallisce, usa il nome dell'evento
    if facts['event_name'] == 'DA DEFINIRE':
        first_part = text.split('.')[0]
        if ' il ' in first_part:
            facts['event_name'] = first_part.split(' il ')[0].strip()
        else:
            facts['event_name'] = first_part[:50].strip()
    
    return facts


# Alias per compatibilità
def extract_facts_enhanced(text: str) -> Dict[str, str]:
    return extract_facts_with_qwen(text)
