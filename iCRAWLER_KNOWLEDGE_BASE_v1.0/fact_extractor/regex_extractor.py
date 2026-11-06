import re
from typing import Dict

def extract_with_regex(text: str) -> Dict[str, str]:
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
    
    # 1. DATA
    date_patterns = [
        r'(\d{1,2}\s*[-–]\s*\d{1,2}\s+[A-Za-z]+)',
        r'(\d{1,2}\s+[A-Za-z]+)',
        r'(\d{4})',
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            facts['date'] = date_match.group(1).strip()
            break
    
    # 2. LOCATION (prima cerca città note)
    CITIES = ['Roma', 'Milano', 'Torino', 'Bologna', 'Firenze', 'Rovigo', 'Venezia', 'Napoli', 'Genova', 'Palermo']
    loc = None
    # Cerca città nel testo
    for city in CITIES:
        if re.search(rf'\b{re.escape(city)}\b', text, re.IGNORECASE):
            loc = city
            break
    # Se non trovata, cerca pattern "a [Città]" o "in [Città]" con città nota
    if not loc:
        for city in CITIES:
            if re.search(rf'(?:a|in|tra)\s+{re.escape(city)}\b', text, re.IGNORECASE):
                loc = city
                break
    # Fallback: pattern generico (ma evita parole come "Birra")
    if not loc:
        match = re.search(r'(?:a|in|tra)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if match:
            candidate = match.group(1).strip()
            # Escludi parole che non sono città
            if candidate.lower() not in ['birra', 'cultura', 'tutta', 'europa']:
                loc = candidate
    facts['location'] = loc if loc else 'DA DEFINIRE'
    
    # 3. TARGET
    target_match = re.search(r'(?:per|rivolto a)\s+([^.,;]+)', text, re.IGNORECASE)
    if target_match:
        facts['target'] = target_match.group(1).strip()
    
    # 4. OBJECTIVE
    obj_match = re.search(r'(?:Obiettivo|Scopo)\s+([^.,;]+)', text, re.IGNORECASE)
    if obj_match:
        facts['objective'] = obj_match.group(1).strip()
    
    # 5. EVENT NAME (prendi la parte prima della prima virgola o prima di " il " o prima di " a [città]")
    event_candidate = text
    # Prima virgola
    if ',' in text:
        event_candidate = text.split(',', 1)[0].strip()
    else:
        # Cerca " il " seguito da data
        date = facts['date']
        if date != 'DA DEFINIRE':
            # Taglia prima della data (cerca " il " + data)
            pattern = rf'\s+il\s+{re.escape(date)}'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                event_candidate = text[:match.start()].strip()
        # Se ancora lungo, taglia prima di "a [città]"
        if not event_candidate or len(event_candidate) < 4:
            loc = facts['location']
            if loc != 'DA DEFINIRE':
                for sep in [f' a {loc}', f' in {loc}', f' at {loc}']:
                    if sep in text:
                        event_candidate = text.split(sep, 1)[0].strip()
                        break
        # Se ancora vuoto, prendi prime 4 parole
        if not event_candidate or len(event_candidate) < 4:
            words = re.findall(r'\b[A-Za-z]+\b', text)
            if words:
                event_candidate = ' '.join(words[:4])
    
    # Pulisci eventuali "Per ..." residui
    event_candidate = re.sub(r'\s*Per\s+.*$', '', event_candidate, flags=re.IGNORECASE)
    # Rimuovi punteggiatura finale
    event_candidate = re.sub(r'[,;.!?]$', '', event_candidate).strip()
    
    facts['event_name'] = event_candidate if event_candidate and len(event_candidate) > 2 else 'DA DEFINIRE'
    
    # 6. HASHTAG
    htag = re.search(r'(#[a-zA-Z0-9_]+)', text)
    if htag:
        facts['hashtag'] = htag.group(1)
    
    return facts
