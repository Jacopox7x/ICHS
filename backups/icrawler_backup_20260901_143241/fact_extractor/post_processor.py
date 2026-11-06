import re
from typing import Dict

MONTHS = {
    'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
    'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre',
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
}

CITIES = [
    'Roma', 'Milano', 'Torino', 'Bologna', 'Firenze', 'Rovigo',
    'Venezia', 'Napoli', 'Genova', 'Palermo', 'Bari', 'Verona',
    'Dallas', 'Melbourne', 'Tokyo', 'Berlin', 'Paris', 'London'
]

def extract_city(text: str) -> str:
    """Estrae la città dal testo."""
    # 1. Pattern "a [Città]" o "in [Città]" (italiano)
    match = re.search(r'(?:a|in)\s+([A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*)', text)
    if match:
        city = match.group(1).strip()
        if city.lower() not in ['città', 'parte', 'tutta', 'europa', 'italia']:
            return city
    # 2. Pattern "at [Città]" (inglese)
    match = re.search(r'at\s+([A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*)', text, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        if city.lower() not in ['città', 'parte', 'tutta', 'europa', 'italia']:
            return city
    # 3. Cerca città nel database
    for city in CITIES:
        if re.search(rf'\b{re.escape(city)}\b', text, re.IGNORECASE):
            return city
    return 'DA DEFINIRE'

def extract_date(text: str) -> str:
    patterns = [
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'(\d{1,2}\s+[A-Za-z]+)(?=\s|\.|,|$)',
        r'(\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            if len(date_str) == 4 and date_str.isdigit():
                if 2000 <= int(date_str) <= 2099:
                    return date_str
            parts = date_str.split()
            if len(parts) >= 2 and parts[-1].lower() in MONTHS:
                return date_str
    return 'DA DEFINIRE'

def extract_objective(text: str) -> str:
    match = re.search(r'(?:Obiettivo|Scopo|objective|goal)[\s:]*([^.,;]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return 'DA DEFINIRE'

def clean_event_name(event_name: str, full_text: str) -> str:
    if not event_name or event_name == 'DA DEFINIRE':
        return 'DA DEFINIRE'
    
    # 1. Rimuovi "Obiettivo" e tutto ciò che segue
    if 'Obiettivo' in event_name:
        event_name = event_name.split('Obiettivo')[0].strip()
    
    # 2. Rimuovi data
    date = extract_date(full_text)
    if date != 'DA DEFINIRE':
        event_name = re.sub(rf'\s*{re.escape(date)}\s*', ' ', event_name)
        event_name = re.sub(r'\s*\d{4}\s*', ' ', event_name)
    
    # 3. Rimuovi città (con o senza preposizione)
    city = extract_city(full_text)
    if city and city != 'DA DEFINIRE':
        event_name = re.sub(rf'\s*(?:a|in|at)\s*{re.escape(city)}\b', '', event_name, flags=re.IGNORECASE)
        event_name = re.sub(rf'\s*{re.escape(city)}\b', '', event_name, flags=re.IGNORECASE)
    
    # 4. Pulisci spazi e articoli (ma non togliere parole)
    event_name = re.sub(r'\s+', ' ', event_name).strip()
    event_name = event_name.strip().strip(',')
    
    # 5. Se il nome è diventato troppo corto, ricostruisci dal testo
    if len(event_name) < 4:
        # Prendi le prime 4 parole che non sono date, città, o preposizioni
        words = re.findall(r'\b[A-Za-z]+\b', full_text)
        clean_words = []
        skip = {'il', 'la', 'lo', 'i', 'gli', 'le', 'del', 'della', 'dei', 'delle', 'di', 'a', 'in', 'at', 'per'}
        for w in words[:10]:
            if w.lower() not in skip and w.lower() not in MONTHS and w not in CITIES and len(w) > 2:
                clean_words.append(w)
            if len(clean_words) >= 3:
                break
        if clean_words:
            return ' '.join(clean_words)
    
    return event_name if len(event_name) > 3 else 'DA DEFINIRE'

def post_process(facts: Dict[str, str], full_text: str) -> Dict[str, str]:
    result = facts.copy()
    
    result['location'] = extract_city(full_text)
    result['date'] = extract_date(full_text)
    
    if result.get('objective') == 'DA DEFINIRE':
        result['objective'] = extract_objective(full_text)
    
    result['event_name'] = clean_event_name(
        result.get('event_name', ''),
        full_text
    )
    
    target = result.get('target', '')
    for prefix in ['Per ', 'rivolto a ', 'for ']:
        if target.startswith(prefix):
            target = target[len(prefix):]
    result['target'] = target.strip()
    
    return result
